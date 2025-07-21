from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import logfire
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import POSTGRES_URL

_engine = create_async_engine(POSTGRES_URL)
logfire.instrument_sqlalchemy(_engine)


async def initialize_database() -> None:
    async with _engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def dispose_database() -> None:
    await _engine.dispose()


@asynccontextmanager
async def spawn_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(_engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            raise


@asynccontextmanager
async def spawn_session_with_transaction() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(_engine) as session, session.begin():
        yield session
