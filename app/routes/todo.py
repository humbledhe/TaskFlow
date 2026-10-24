from fastapi import APIRouter, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from uuid import UUID

from app.core.dependencies import DbDependency, CurrentUserDependency
from app.services.todo import TodoSerivces
from app.schemas.todo import (
    TodoCreateModel,
    TodoUpdateModel,
    TodoResponseModel,
    Response,
    FilterQuery,
)
from app.models.user import User

router = APIRouter()


@router.get("", response_model=Response[list[TodoResponseModel]])
async def get_todos(
    query: Annotated[FilterQuery, Query()],
    current_user: CurrentUserDependency,
    session: DbDependency,
):
    todos = await TodoSerivces.get_todos(
        query=query, current_user=current_user, session=session
    )

    return {"data": todos}


@router.get("/{todo_uid}", response_model=Response[TodoResponseModel])
async def get_todo(
    todo_uid: UUID, current_user: CurrentUserDependency, session: DbDependency
):
    todo_services = TodoSerivces()

    todo = await todo_services.get_todo(
        todo_uid=todo_uid, current_user=current_user, session=session
    )

    return {"data": todo}


@router.post(
    "", response_model=Response[TodoResponseModel], status_code=status.HTTP_201_CREATED
)
async def create_todo(
    new_todo: TodoCreateModel,
    current_user: CurrentUserDependency,
    session: DbDependency,
):
    new_todo = await TodoSerivces.create_todo(
        new_todo=new_todo, current_user=current_user, session=session
    )

    return {"data": new_todo}


@router.patch("/{todo_uid}", response_model=Response[TodoResponseModel])
async def update_todo(
    todo_uid: UUID,
    update_todo: TodoUpdateModel,
    current_user: CurrentUserDependency,
    session: DbDependency,
):
    todo_services = TodoSerivces()

    updated_todo = await todo_services.update_todo(
        todo_uid=todo_uid,
        update_todo=update_todo,
        current_user=current_user,
        session=session,
    )

    return {"data": updated_todo}


@router.delete("/{todo_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_uid: UUID, current_user: CurrentUserDependency, session: DbDependency
):
    todo_services = TodoSerivces()

    await todo_services.delete_todo(
        todo_uid=todo_uid, current_user=current_user, session=session
    )

    return {"detail": "Todo deleted successfully"}
