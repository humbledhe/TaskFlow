from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.exceptions import UserNotFoundError
from app.core.security import hash


class UserService:
    async def get_users(self, session: AsyncSession):
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()

        return users

    async def get_user(self, user_uid: UUID, session: AsyncSession):
        stmt = select(User).where(User.public_id == user_uid)
        result = await session.execute(stmt)
        user = result.scalar()

        return user

    async def create_user(self, user_data: UserCreate, session: AsyncSession):
        user_password = user_data.password_hash

        hashed_password = hash(user_password)

        user_data.password_hash = hashed_password

        user = User(**user_data.model_dump())

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    async def delete_user(self, user_uid: UUID, session: AsyncSession):
        stmt = delete(User).where(User.public_id == user_uid)
        result = await session.execute(stmt)

        if result.rowcount == 0:
            raise UserNotFoundError(
                "The requested user cannot be found or does not exist"
            )

        await session.commit()
