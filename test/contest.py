import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import ASGITransport, AsyncClient

from collections.abc import AsyncGenerator
import os

from app.models import Base
from app.core.dependencies import get_async_db
from app.main import app

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://humbledhe:postgres@localhost:5432/taskflow_test_db"
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine():
    url = os.environ["DATABASE_URL"]

    if "test" not in url.rsplit("/", 1)[-1]:
        raise RuntimeError(
            "Unexpected database. Refusing to run tests on a non-test database"
        )

    engine = create_async_engine(url)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.connect() as connection:
        outer_transaction = await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_factory() as session:
            try:
                yield session
            finally:
                session.close()

        await outer_transaction.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_async_db():
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_async_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop[get_async_db, None]
