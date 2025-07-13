from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import dispose_database, initialize_database
from app.service.search.client import dispose_elastic, initialize_elastic


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    await initialize_database()
    await initialize_elastic()

    yield

    await dispose_database()
    await dispose_elastic()
