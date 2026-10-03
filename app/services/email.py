import aiosmtplib
from email.message import EmailMessage
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

import secrets
from datetime import datetime, timezone, timedelta

from app.core.config import settings
from app.core.security import hash, verify
from app.core.exceptions import (
    InvalidOTPError,
    UserAlreadyVerifiedError,
    ExpiredOTPError,
)
from app.models.email_verification import EmailVerification
from app.models.user import User
from app.schemas.email import OTPCreate, OTPVerify, OTPSend
from .user import UserService


def generate_otp() -> str:
    """Generate a cryptographically secure six-digit OTP."""
    otp = secrets.randbelow(900000) + 100000

    return str(otp)


class EmailService:
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

    async def send_otp(self, otp_send: OTPSend, session: AsyncSession):
        """Generate, persist, and email an account-verification OTP."""
        user_public_id = otp_send.user_public_id

        stmt = select(User).where(User.public_id == user_public_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user.is_verified == True:
            raise UserAlreadyVerifiedError("User is already verified")

        prev_otp = await self.get_stored_otp(user.id, session)

        if prev_otp:
            is_expired = prev_otp.expires_at <= datetime.now(timezone.utc)

            if is_expired:
                await session.execute(
                    delete(EmailVerification).where(
                        EmailVerification.user_id == user.id
                    )
                )

                await session.commit()

        otp = generate_otp()

        # Store only the hash. The plaintext OTP should never be persisted.
        hashed_otp = hash(otp)

        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=5)

        otp_create_data = OTPCreate(
            token_hash=hashed_otp,
            user_id=user.id,
            created_at=now,
            expires_at=expires,
        )

        email_verification_data = EmailVerification(**otp_create_data.model_dump())

        session.add(email_verification_data)

        await session.commit()

        user_email = user.email
        subject = otp_send.subject

        await self.send_email(to=user_email, body=otp, subject=subject)

        return otp

    async def get_stored_otp(self, user_id: int, session: AsyncSession):
        """Return the user's current email-verification record."""
        stmt = select(EmailVerification).where(EmailVerification.user_id == user_id)
        result = await session.execute(stmt)
        otp = result.scalar()

        return otp

    async def verify_otp(self, otp_vefify: OTPVerify, session: AsyncSession):
        """Verify an OTP and mark the user's email as verified."""
        user_public_id = otp_vefify.user_public_id

        user_service = UserService()

        user = await user_service.get_user(user_public_id, session)
        otp = await self.get_stored_otp(user.id, session)

        user_otp = otp_vefify.token_hash
        correct_otp = otp.token_hash

        # The submitted OTP is plaintext; the stored value is its hash.
        if verify(user_otp, correct_otp):
            is_expired = otp.expires_at <= datetime.now(timezone.utc)

            if is_expired:
                await session.execute(
                    delete(EmailVerification).where(
                        EmailVerification.user_id == user.id
                    )
                )

                await session.commit()

                raise InvalidOTPError("Invalid or expired verification code")

            verified_at = datetime.now(timezone.utc)

            await session.execute(
                update(EmailVerification)
                .where(EmailVerification.user_id == user.id)
                .values(verified_at=verified_at)
            )

            await session.commit()

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
