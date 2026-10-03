from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from uuid import UUID
from datetime import datetime, timezone, timedelta

from app.models.user import User
from app.schemas.auth import AuthUser
from app.core.exceptions import InvalidCredentialsError, UserNotVerifiedError
from app.core.security import verify, create_access_token

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRY_MINUTES = 240


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

        stmt = select(User).where(User.email == email)
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

        now = datetime.now(timezone.utc)
        access_token_expiry = int(
            (now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
        )

        user_data = {
            "sub": str(user.public_id),
            "iat": int(now.timestamp()),
            "exp": access_token_expiry,
            "type": "access",
        }

        access_token = create_access_token(user_data, access_token_expiry)

        refresh_token_expiry = int(
            (now + timedelta(minutes=REFRESH_TOKEN_EXPIRY_MINUTES)).timestamp()
        )
        user_data["exp"] = refresh_token_expiry
        user_data["type"] = "refresh"

        refresh_token = create_access_token(
            user_data, refresh_token_expiry, refresh=True
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }
