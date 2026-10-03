from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from uuid import UUID

from app.core.dependencies import get_async_db, get_current_user
from app.services.todo import TodoSerivces
from app.schemas.todo import (
    TodoCreateModel,
    TodoUpdateModel,
    TodoResponseModel,
    Response,
)
from app.models.user import User

router = APIRouter()
todo_services = TodoSerivces()

DbDependency = Annotated[AsyncSession, Depends(get_async_db)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=Response[list[TodoResponseModel]])
async def get_todos(current_user: CurrentUserDependency, session: DbDependency):
    todos = await todo_services.get_todos(current_user, session)

    return {"data": todos}


@router.get("/{todo_uid}", response_model=Response[TodoResponseModel])
async def get_todo(
    todo_uid: UUID, current_user: CurrentUserDependency, session: DbDependency
):
    todo = await todo_services.get_todo(todo_uid, current_user, session)

    return {"data": todo}


@router.post(
    "/", response_model=Response[TodoResponseModel], status_code=status.HTTP_201_CREATED
)
async def create_todo(
    new_todo: TodoCreateModel,
    current_user: CurrentUserDependency,
    session: DbDependency,
):
    new_todo = await todo_services.create_todo(new_todo, current_user, session)

    return {"data": new_todo}


@router.put("/{todo_uid}", response_model=Response[TodoResponseModel])
async def update_todo(
    todo_uid: UUID,
    update_todo: TodoUpdateModel,
    current_user: CurrentUserDependency,
    session: DbDependency,
):
    updated_todo = await todo_services.update_todo(
        todo_uid, update_todo, current_user, session
    )

    return {"data": updated_todo}


@router.delete("/{todo_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_uid: UUID, current_user: CurrentUserDependency, session: DbDependency
):
    await todo_services.delete_todo(todo_uid, current_user, session)

    return {"detail": "Todo deleted successfully"}
