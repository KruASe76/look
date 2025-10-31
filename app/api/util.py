import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

import logfire
from fastapi import FastAPI

from app.database import dispose_database, initialize_database, setup_notifications
from app.service import listen, warmup
from app.service.search.client import dispose_elastic, initialize_elastic


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    with logfire.span("App startup"):
        await initialize_database()
        await setup_notifications()
        await initialize_elastic()

        await warmup()

    listen_task = asyncio.create_task(listen())

    yield

    with logfire.span("App shutdown"):
        await dispose_database()
        await dispose_elastic()

        listen_task.cancel()
        with suppress(asyncio.CancelledError):
            await listen_task
