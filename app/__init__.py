__all__ = ["main"]

from typing import Annotated

import logfire
import typer
import uvicorn

from .api import app
from .core.config import LOGFIRE_ENVIRONMENT, LOGFIRE_SERVICE_NAME


def main(
    host: Annotated[str, typer.Option(envvar="APP_HOST")] = "localhost",
    port: Annotated[int, typer.Option(envvar="APP_PORT")] = 8000,
    *,
    reload: Annotated[bool, typer.Option(help="Enable hot-reload")] = False,
) -> None:
    logfire.configure(
        service_name=LOGFIRE_SERVICE_NAME,
        environment=LOGFIRE_ENVIRONMENT,
        send_to_logfire="if-token-present",
    )

    logfire.instrument_pydantic()
    logfire.instrument_fastapi(app)

    uvicorn.run(f"{__name__}:app", host=host, port=port, reload=reload)


def cli() -> None:
    typer.run(main)
