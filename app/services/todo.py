from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.models.todo import Todo
from app.schemas.todo import TodoCreateModel, TodoUpdateModel


class TodoSerivces:
    async def get_todos(self, session: AsyncSession):
        stmt = select(Todo)
        result = await session.execute(stmt)
        todos = result.scalars().all()

        return todos

    async def get_todo(self, todo_uid: UUID, session: AsyncSession):
        stmt = select(Todo).where(Todo.id == todo_uid)
        result = await session.execute(stmt)
        todo = result.scalar()

        return todo

    async def create_todo(self, new_todo: TodoCreateModel, session: AsyncSession):
        todo = Todo(**new_todo.model_dump())

        session.add(todo)
        await session.commit()
        await session.refresh(todo)

        return todo

    async def update_todo(
        self, todo_uid: UUID, update_todo: TodoUpdateModel, session: AsyncSession
    ):
        stmt = (
            update(Todo)
            .where(Todo.id == todo_uid)
            .values(**update_todo.model_dump())
            .returning(Todo)
        )
        result = await session.execute(stmt)
        updated_todo = result.scalars().first()

        await session.commit()

        return updated_todo

    async def delete_todo(self, todo_uid: UUID, session: AsyncSession):
        stmt = delete(Todo).where(Todo.id == todo_uid)
        result = await session.execute(stmt)

        await session.commit()
