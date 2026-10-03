from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.core.dependencies import get_async_db
from app.services.auth import AuthService
from app.schemas.auth import AuthUser, Response, AuthResponse

router = APIRouter()

auth_service = AuthService()

DbDependency = Annotated[AsyncSession, Depends(get_async_db)]
LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post("/login", response_model=Response[AuthResponse])
async def login_user(login_form: LoginForm, session: DbDependency):
    authenticated_user = await auth_service.login_user_for_token(login_form, session)

    return {"data": authenticated_user}
    
