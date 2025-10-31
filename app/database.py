__all__ = [
    "dispose_database",
    "initialize_database",
    "setup_notifications",
    "spawn_readonly_session",
    "spawn_session_with_transaction",
    "start_readonly_session",
    "start_transaction",
]

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
import logfire
import pg_async_events
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import ASYNCPG_URL, SQLALCHEMY_URL

_engine = create_async_engine(SQLALCHEMY_URL)
logfire.instrument_sqlalchemy(_engine)


async def initialize_database() -> None:
    async with _engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def setup_notifications() -> None:
    # noinspection PyUnresolvedReferences
    pool = await asyncpg.create_pool(ASYNCPG_URL, min_size=1, max_size=2)
    await pg_async_events.initialize(pool)


async def dispose_database() -> None:
    await _engine.dispose()


async def spawn_readonly_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(_engine) as session:
        yield session
        await session.rollback()


async def spawn_session_with_transaction() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(_engine) as session, session.begin():
        yield session


start_readonly_session = asynccontextmanager(spawn_readonly_session)
start_transaction = asynccontextmanager(spawn_session_with_transaction)
