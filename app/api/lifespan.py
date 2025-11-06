import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

import logfire
from fastapi import FastAPI

from app.core.config import LOGFIRE_ENVIRONMENT, LOGFIRE_SERVICE_NAME
from app.database import dispose_database, initialize_database, setup_notifications
from app.service import listen, warmup
from app.service.search.client import dispose_elastic, initialize_elastic

from .route import setup_routing


def setup_logfire(fastapi_app: FastAPI) -> None:
    logfire.configure(
        service_name=LOGFIRE_SERVICE_NAME,
        environment=LOGFIRE_ENVIRONMENT,
        send_to_logfire="if-token-present",
        distributed_tracing=False,
        console=logfire.ConsoleOptions(min_log_level="debug"),
    )

    logfire.instrument_pydantic()
    logfire.instrument_fastapi(fastapi_app)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None]:
    setup_logfire(fastapi_app)

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
