import aiosmtplib
from email.message import EmailMessage
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

import secrets
from datetime import datetime, timezone, timedelta
from uuid import UUID

from app.core.config import settings
from app.core.security import hash_otp
from app.core.exceptions import (
    InvalidOTPError,
    UserAlreadyVerifiedError,
    ExpiredOTPError,
    UserNotFoundError,
)
from app.models.email_verification import EmailVerification
from app.models.user import User
from .user import UserService


def generate_otp() -> str:
    """Generate a cryptographically secure six-digit OTP."""
    otp = secrets.randbelow(900000) + 100000

    return str(otp)


async def store_otp_digest(
    otp_digest: str, purpose: str, user_id: str, ex: int, redis: Redis
):
    await redis.set(name=f"otp:{purpose}:{user_id}", value=otp_digest, ex=ex)


async def get_stored_otp_digest(purpose: str, user_id: str, redis: Redis):
    otp_digest = await redis.get(name=f"otp:{purpose}:{user_id}")

    return otp_digest


class EmailVerificationService:
    """Handle email delivery and email verification."""

    async def send_email(self, *, to: str, body: str, subject: str) -> None:
        """Send a plain-text email through the configured SMTP server."""
        message = EmailMessage()

        message["from"] = settings.MAIL_FROM
        message["TO"] = to
        message["SUBJECT"] = subject

        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )

    async def send_otp(
        self, user_public_id: UUID, session: AsyncSession, redis: Redis
    ) -> None:
        """Generate, persist, and email an account-verification OTP."""

        stmt = select(User).where(User.public_id == user_public_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise UserNotFoundError("User does not exist")

        otp = generate_otp()

        # Store only the hash. The plaintext OTP should never be persisted.
        otp_digest = hash_otp(otp, "email-verification", str(user.public_id))

        await store_otp_digest(
            otp_digest=otp_digest,
            purpose="email-verification",
            user_id=str(user.public_id),
            ex=300,
            redis=redis,
        )

        await self.send_email(
            to=user.email, body=otp, subject="Verify your email address"
        )

    async def verify_otp(
        self, user_public_id: UUID, code: str, session: AsyncSession, redis: Redis
    ):
        """Verify an OTP and mark the user's email as verified."""

        stmt = select(User).where(User.public_id == user_public_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise UserNotFoundError("User does not exist")

        submitted_otp = hash_otp(
            otp=code, purpose="email-verification", user_id=str(user_public_id)
        )
        stored_otp_digest = await get_stored_otp_digest(
            purpose="email-verification", user_id=str(user_public_id), redis=redis
        )

        # The submitted OTP and stored otp are both hashed and compared
        if submitted_otp == stored_otp_digest:
            verified_at = datetime.now(timezone.utc)

            stmt = (
                update(User)
                .where(User.id == user.id)
                .values(is_verified=True)
                .returning(User)
            )
            result = await session.execute(stmt)
            user = result.scalar_one()

            await session.commit()

            return user

        raise InvalidOTPError("Invalid or expired verification code")
