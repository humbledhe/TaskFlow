from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.exceptions import UserNotFoundError, EmailAlreadyExistsError
from app.core.security import hash


class UserService:
    async def get_user(self, user_uid: UUID, session: AsyncSession):
        stmt = (
            select(User)
            .where(User.public_id == user_uid)
            .options(selectinload(User.todos))
        )
        result = await session.execute(stmt)
        user = result.scalar()

        return user

    @staticmethod
    async def create_user(user_data: UserCreate, session: AsyncSession) -> User:
        hashed_password = hash(user_data.password)

        user = User(
            **user_data.model_dump(exclude={"password"}), password_hash=hashed_password
        )

        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            await session.rollback()
            raise EmailAlreadyExistsError("Email already exists. Please Login")

        return user

    @staticmethod
    async def delete_user(current_user: User, session: AsyncSession) -> None:
        await session.delete(current_user)
        await session.commit()
