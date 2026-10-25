from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis

from uuid import UUID, uuid7
from datetime import datetime, timezone, timedelta

from app.models.user import User
from app.schemas.email_verification import OTPSend
from app.core.exceptions import InvalidCredentialsError, UserNotVerifiedError
from app.core.security import verify
from .email_verification import EmailVerificationService
from app.core.config import settings


async def add_jwt_to_blocklist(jti: str, redis: Redis) -> None:
    await redis.set(
        name=f"jwt:blocklist:{jti}", value="1", exat=15
    )  # Error at exat access_token_expiry


async def token_in_blocklist(jti: str, redis: Redis) -> bool:
    jti = await redis.get(name=f"jwt:blocklist:{jti}")

    return jti is not None


class AuthService:
    @staticmethod
    async def authenticate_user(
        form_data: OAuth2PasswordRequestForm, session: AsyncSession
    ):
        """Authenticate a user using their email and password.

        Raises:
            InvalidCredentialsError: If the email does not exist or the
                provided password is incorrect.

        Returns:
            User: The authenticated user.
        """
        email = form_data.username
        password = form_data.password

        stmt = select(User).where(User.email == email).options(selectinload(User.todos))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise InvalidCredentialsError("Invalid email or password")

        correct_password = user.password_hash

        if not verify(password, correct_password):
            raise InvalidCredentialsError("Invalid email or password")

        return user

    async def forget_password_reset_otp(otp_send: OTPSend, session: AsyncSession):
        email_verification_service = EmailVerificationService()

        await email_verification_service.send_otp(otp_send, session)

    @staticmethod
    async def logout_user(token_details: dict, redis: Redis) -> None:
        jti = token_details["jti"]

        await add_jwt_to_blocklist(jti, redis)
