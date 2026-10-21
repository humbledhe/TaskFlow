from typing import Annotated, AsyncGenerator

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session
from app.models.user import User
from app.services.auth import token_in_blocklist

from .security import decode_token
from .exceptions import (
    InvalidAccessTokenError,
    InvalidRefreshTokenError,
    RevokedAccessTokenError,
    UserNotVerifiedError,
)


# --------------------------------------------------
# Database
# --------------------------------------------------


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


DbDependency = Annotated[
    AsyncSession,
    Depends(get_async_db),
]


# --------------------------------------------------
# Redis
# --------------------------------------------------


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


RedisDependency = Annotated[
    Redis,
    Depends(get_redis),
]


# --------------------------------------------------
# Shared token validation
# --------------------------------------------------


async def validate_token(
    token: str,
    redis: Redis,
    expected_type: str,
) -> dict:
    token_data = decode_token(token)

    if not token_data:
        if expected_type == "access":
            raise InvalidAccessTokenError("Invalid access token")

        raise InvalidRefreshTokenError("Invalid refresh token")

    if token_data.get("type") != expected_type:
        if expected_type == "access":
            raise InvalidAccessTokenError("Invalid access token")

        raise InvalidRefreshTokenError("Invalid refresh token")

    if not all(token_data.get(claim) for claim in ("sub", "jti", "exp")):
        if expected_type == "access":
            raise InvalidAccessTokenError("Invalid access token")

        raise InvalidRefreshTokenError("Invalid refresh token")

    if await token_in_blocklist(token_data["jti"], redis):
        if expected_type == "access":
            raise RevokedAccessTokenError("Access token has been revoked")

        raise InvalidRefreshTokenError("Refresh token has been revoked")

    return token_data


# --------------------------------------------------
# Authentication
# --------------------------------------------------


class TokenBearer(HTTPBearer):
    def __init__(self, expected_type: str):
        super().__init__(auto_error=False)
        self.expected_type = expected_type

    async def __call__(
        self,
        request: Request,
        redis: RedisDependency,
    ) -> dict:
        cookie_name = (
            "access_token" if self.expected_type == "access" else "refresh_token"
        )

        # Prefer the appropriate HTTP-only cookie.
        token = request.cookies.get(cookie_name)

        print("Request URL:", request.url)
        print("Cookie names received:", list(request.cookies.keys()))
        print("Expected cookie:", cookie_name)
        print("Cookie received:", token is not None)

        # Fall back to Swagger's Authorization header.
        if not token:
            credentials = await super().__call__(request)

            if credentials is not None:
                token = credentials.credentials

        if not token:
            if self.expected_type == "access":
                raise InvalidAccessTokenError("Access token is missing")

            raise InvalidRefreshTokenError("Refresh token is missing")

        return await validate_token(
            token=token,
            redis=redis,
            expected_type=self.expected_type,
        )


access_token_bearer = TokenBearer("access")
refresh_token_bearer = TokenBearer("refresh")


Credentials = Annotated[
    dict,
    Depends(access_token_bearer),
]

RefreshCredentials = Annotated[
    dict,
    Depends(refresh_token_bearer),
]


# --------------------------------------------------
# Current user
# --------------------------------------------------


async def get_current_user(
    credentials: Credentials,
    session: DbDependency,
) -> User:
    stmt = select(User).where(User.public_id == credentials["sub"])

    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise InvalidAccessTokenError(
            "The user associated with this token no longer exists"
        )

    return user


CurrentUserDependency = Annotated[
    User,
    Depends(get_current_user),
]
