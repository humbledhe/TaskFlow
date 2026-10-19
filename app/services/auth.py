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
from app.core.security import verify, create_access_token
from .email_verification import EmailVerificationService

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRY_MINUTES = 240

now = datetime.now(timezone.utc)

access_token_expiry = int(
    (now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
)
refresh_token_expiry = int(
    (now + timedelta(minutes=REFRESH_TOKEN_EXPIRY_MINUTES)).timestamp()
)


async def add_jwt_to_blocklist(jti: str, redis: Redis) -> None:
    await redis.set(name=f"jwt:blocklist:{jti}", value="1", exat=access_token_expiry)


async def token_in_blocklist(jti: str, redis: Redis) -> bool:
    jti = await redis.get(name=f"jwt:blocklist:{jti}")

    return jti is not None


class AuthService:
    async def authenticate_user(
        self, login_form: OAuth2PasswordRequestForm, session: AsyncSession
    ):
        """Authenticate a user using their email and password.

        Raises:
            InvalidCredentialsError: If the email does not exist or the
                provided password is incorrect.

        Returns:
            User: The authenticated user.
        """
        email = login_form.username
        password = login_form.password

        stmt = select(User).where(User.email == email).options(selectinload(User.todos))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_verified:
            raise UserNotVerifiedError("User account has not been verified")

        correct_password = user.password_hash

        if not verify(password, correct_password):
            raise InvalidCredentialsError("Invalid email or password")

        return user

    async def login_user_for_token(
        self, login_form: OAuth2PasswordRequestForm, session: AsyncSession
    ):
        """Authenticate a user and generate access and refresh tokens.

        Raises:
            InvalidCredentialsError: If the supplied credentials are invalid.

        Returns:
            dict: The generated access token, refresh token, and user.
        """
        user = await self.authenticate_user(login_form, session)

        user_data = {
            "sub": str(user.public_id),
            "jti": str(uuid7()),
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": access_token_expiry,
        }

        access_token = create_access_token(user_data)

        user_data["exp"] = refresh_token_expiry
        user_data["type"] = "refresh"

        refresh_token = create_access_token(user_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }

    async def forget_password_reset_otp(otp_send: OTPSend, session: AsyncSession):
        email_verification_service = EmailVerificationService()

        await email_verification_service.send_otp(otp_send, session)

    async def logout_user(self, token_details: dict, redis: Redis) -> None:
        jti = token_details["jti"]

        await add_jwt_to_blocklist(jti, redis)
