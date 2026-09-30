from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from uuid import UUID

from app.core.dependencies import get_async_db
from app.core.exceptions import TodoNotFoundError
from app.services.todo import TodoSerivces
from app.schemas.todo import TodoCreateModel, TodoUpdateModel

router = APIRouter()
todo_services = TodoSerivces()

DbDependency = Annotated[AsyncSession, Depends(get_async_db)]


@router.get("/")
async def get_todos(session: DbDependency):
    todos = await todo_services.get_todos(session)

    return todos


@router.get("/{todo_uid}")
async def get_todo(todo_uid: UUID, session: DbDependency):
    todo = await todo_services.get_todo(todo_uid, session)

    return todo


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(new_todo: TodoCreateModel, session: DbDependency):
    new_todo = await todo_services.create_todo(new_todo, session)

    return new_todo


@router.put("/{todo_uid}")
async def update_todo(
    todo_uid: UUID, update_todo: TodoUpdateModel, session: DbDependency
):
    todo = await todo_services.get_todo(todo_uid, session)

    if not todo:
        raise TodoNotFoundError("Todo does not exist")

    updated_todo = await todo_services.update_todo(todo_uid, update_todo, session)

    return updated_todo


@router.delete("/{todo_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_uid: UUID, session: DbDependency):
    todo = await todo_services.get_todo(todo_uid, session)

    if not todo:
        raise TodoNotFoundError("Todo does not exist")

    await todo_services.delete_todo(todo_uid, session)

    return {"detail": "Todo deleted successfully"}
