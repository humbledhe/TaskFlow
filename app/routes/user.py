from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from uuid import UUID

from app.core.dependencies import get_async_db
from app.services.user import UserService
from app.schemas.user import UserCreate, UserResponse, Response

router = APIRouter()

user_service = UserService()

DbDependency = Annotated[AsyncSession, Depends(get_async_db)]


@router.get("", response_model=Response[list[UserResponse]])
async def get_users(session: DbDependency):
    users = await user_service.get_users(session)

    return {"data": users}


@router.get("/{user_uid}", response_model=Response[UserResponse])
async def get_user(user_uid: UUID, session: DbDependency):
    users = await user_service.get_user(user_uid, session)

    return {"data": users}


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=Response[UserResponse]
)
async def create_user(user_data: UserCreate, session: DbDependency):
    new_user = await user_service.create_user(user_data, session)

    return {"data": new_user}


@router.delete("/{user_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def get_user(user_uid: UUID, session: DbDependency):
    await user_service.delete_user(user_uid, session)

    return {"detail": "User has been deleted successfully"}
