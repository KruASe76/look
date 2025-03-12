__all__ = ["lifespan"]

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import dispose_database, initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    await initialize_database()

    yield

    await dispose_database()
