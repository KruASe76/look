__all__ = ["dispose_database", "initialize_database", "spawn_session", "spawn_session_transaction"]

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSessionTransaction, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import POSTGRES_URL

engine = create_async_engine(POSTGRES_URL)


async def initialize_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def dispose_database() -> None:
    await engine.dispose()


async def spawn_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session


async def spawn_session_transaction() -> AsyncGenerator[AsyncSessionTransaction]:
    async with AsyncSession(engine).begin() as session:
        yield session
