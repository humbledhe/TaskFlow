from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import TodoCreateModel, TodoUpdateModel
from app.core.exceptions import TodoNotFoundError, UserNotVerifiedError


class TodoSerivces:
    async def get_todos(self, current_user: User, session: AsyncSession) -> list[Todo]:
        stmt = select(Todo).where(Todo.user_id == current_user.id)
        result = await session.execute(stmt)
        todos = result.scalars().all()

        return todos

    async def get_todo(
        self, todo_uid: UUID, current_user: User, session: AsyncSession
    ) -> Todo:
        stmt = (
            select(Todo)
            .where(Todo.user_id == current_user.id)
            .where(Todo.public_id == todo_uid)
        )
        result = await session.execute(stmt)
        todo = result.scalar_one_or_none()

        return todo

    async def create_todo(
        self, new_todo: TodoCreateModel, current_user: User, session: AsyncSession
    ) -> Todo:
        todo = Todo(user_id=current_user.id, **new_todo.model_dump())

        session.add(todo)
        await session.commit()
        await session.refresh(todo)

        return todo

    async def update_todo(
        self,
        todo_uid: UUID,
        update_todo: TodoUpdateModel,
        current_user: User,
        session: AsyncSession,
    ) -> Todo:
        user_id = current_user.id

        stmt = (
            update(Todo)
            .where(Todo.user_id == current_user.id)
            .where(Todo.public_id == todo_uid)
            .values(**update_todo.model_dump())
            .returning(Todo)
        )
        result = await session.execute(stmt)
        updated_todo = result.scalars().first()

        if updated_todo is None:
            raise TodoNotFoundError("Todo does not exist")

        await session.commit()

        return updated_todo

    async def delete_todo(
        self, todo_uid: UUID, current_user: User, session: AsyncSession
    ) -> None:
        stmt = (
            delete(Todo)
            .where(Todo.user_id == current_user.id)
            .where(Todo.public_id == todo_uid)
        )
        result = await session.execute(stmt)

        if result.rowcount == 0:
            raise TodoNotFoundError("Todo does not exist")

        await session.commit()
