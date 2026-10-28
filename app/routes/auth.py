from fastapi import APIRouter, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid7

from app.core.dependencies import DbDependency, Credentials, RedisDependency
from app.core.exceptions import UserNotVerifiedError
from app.services.auth import AuthService

# from app.schemas.auth import Response, AuthResponse
from app.core.security import create_jwt_token
from app.core.config import settings

router = APIRouter()
# auth_service = AuthService()


@router.post(
    "/login",
    summary="Authenticate a user",
    description=(
        "Authenticates a user using their email and password. "
        "On success, sets access and refresh tokens in HTTP-only "
        "cookies and returns a success message."
    ),  # response_model=Response[AuthResponse]
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DbDependency,
):
    user = await AuthService.authenticate_user(form_data, session)

    now = datetime.now(timezone.utc)

    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_MINUTES = 240

    access_token_expiry = int(
        (now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
    )
    refresh_token_expiry = int(
        (now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)).timestamp()
    )

    user_data = {
        "sub": str(user.public_id),
        "jti": str(uuid7()),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": access_token_expiry,
    }

    access_token = create_jwt_token(user_data)

    user_data = {
        "sub": str(user.public_id),
        "jti": str(uuid7()),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": refresh_token_expiry,
    }

    refresh_token = create_jwt_token(user_data)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return {"message": "Login successful"}


# @router.post("/forget-password-reset")
# async def password_reset(session: DbDependency):
#     pass


# @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
# async def logout(token_details: Credentials, redis: RedisDependency):
#     await AuthService.logout_user(token_details, redis)

#     return {"message": "User logged out successfully"}
