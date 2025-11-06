import asyncio
from typing import Annotated

import uvicorn
from typer import Option, Typer

from .bot import run_polling

cli = Typer()


@cli.command()
def run(
    host: Annotated[str, Option(envvar="APP_HOST")] = "localhost",
    port: Annotated[int, Option(envvar="APP_PORT")] = 8000,
    *,
    polling: Annotated[bool, Option(help="Run in polling mode")] = False,
) -> None:
    if polling:
        asyncio.run(run_polling())
    else:
        uvicorn.run(
            "bot:app",
            host=host,
            port=port,
        )


def main() -> None:
    """Shell script entrypoint."""
    cli()


if __name__ == "__main__":
    main()
