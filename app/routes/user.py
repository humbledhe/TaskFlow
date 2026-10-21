from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from uuid import UUID

from app.core.dependencies import DbDependency, CurrentUserDependency
from app.services.user import UserService
from app.schemas.user import UserCreate, UserResponse, Response

router = APIRouter()


@router.get("/me", response_model=Response[UserResponse])
async def get_user(current_user: CurrentUserDependency):
    return {"data": current_user}


@router.post(
    "/create-account",
    status_code=status.HTTP_201_CREATED,
    response_model=Response[UserResponse],
)
async def create_user(user_data: UserCreate, session: DbDependency):
    new_user = await UserService.create_user(user_data, session)

    return {"data": new_user}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_user(current_user: CurrentUserDependency, session: DbDependency):
    await UserService.delete_user(current_user, session)

    return {"detail": "User has been deleted successfully"}
