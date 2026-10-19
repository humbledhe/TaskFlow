from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.core.dependencies import DbDependency, Credentials, RedisDependency
from app.services.auth import AuthService
from app.schemas.auth import Response, AuthResponse

router = APIRouter()
auth_service = AuthService()

LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/login", response_model=Response[AuthResponse])
async def login_user(login_form: LoginForm, session: DbDependency):
    authenticated_user = await auth_service.login_user_for_token(login_form, session)

    return {"data": authenticated_user}


@router.post("/forget-password-reset")
async def password_reset(session: DbDependency):
    pass


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token_details: Credentials, redis: RedisDependency):
    await auth_service.logout_user(token_details, redis)

    return {"message": "User logged out successfully"}
