from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Depends
from fastapi.security import HTTPBearer

from typing import AsyncGenerator, Annotated

from app.database.session import async_session
from app.models.user import User
from .security import decode_token
from .exceptions import InvalidAccessTokenError, InvalidRefreshTokenError


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


DbDependency = Annotated[AsyncSession, Depends(get_async_db)]


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)

        if token_data is None:
            raise InvalidAccessTokenError("Invalid access token")

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please implement this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data["user"]["type"] == "refresh":
            raise InvalidAccessTokenError("Invalid access token")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data["user"]["type"] == "access":
            raise InvalidRefreshTokenError("Invalid refresh token")


Credentials = Annotated[dict, Depends(AccessTokenBearer())]


async def get_current_user(credentials: Credentials, session: DbDependency) -> User:
    user_public_id = credentials["user"]["sub"]

    stmt = select(User).where(User.public_id == user_public_id)
    result = await session.execute(stmt)
    user = result.scalar_one()

    return user
