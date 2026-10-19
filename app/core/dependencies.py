from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Depends
from fastapi.security import HTTPBearer
from redis.asyncio import Redis

from typing import AsyncGenerator, Annotated

from app.database.session import async_session
from app.models.user import User
from .security import decode_token
from .exceptions import (
    InvalidAccessTokenError,
    InvalidRefreshTokenError,
    UserNotVerifiedError,
    RevokedAccessTokenError,
)
from app.services.auth import token_in_blocklist


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


DbDependency = Annotated[AsyncSession, Depends(get_async_db)]


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


RedisDependency = Annotated[Redis, Depends(get_redis)]


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, redis: RedisDependency) -> dict:
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)

        if token_data is None:
            raise InvalidAccessTokenError("Invalid access token")

        self.verify_token_data(token_data)

        if await token_in_blocklist(token_data["jti"], redis):
            raise RevokedAccessTokenError("This token has been revoked")

        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please implement this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data["type"] == "refresh":
            raise InvalidAccessTokenError("Invalid access token")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data["type"] == "access":
            raise InvalidRefreshTokenError("Invalid refresh token")


Credentials = Annotated[dict, Depends(AccessTokenBearer())]


async def get_current_user(credentials: Credentials, session: DbDependency) -> User:
    user_public_id = credentials["sub"]

    stmt = select(User).where(User.public_id == user_public_id)
    result = await session.execute(stmt)
    user = result.scalar_one()

    return user


CurrentUserDependency = Annotated[User, Depends(get_current_user)]


# class RoleChecker:
#     def __call__(self, current_user: CurrentUser):
#         if not current_user.is_verified:
#             raise UserNotVerifiedError("User account has not been verified")
