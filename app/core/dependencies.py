from sqlalchemy.ext.asyncio import AsyncSession

from typing import AsyncGenerator

from app.database.session import async_session


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
