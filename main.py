from typing import Annotated

import typer
import uvicorn


def main(
    host: Annotated[str, typer.Option(envvar="APP_HOST")] = "localhost",
    port: Annotated[int, typer.Option(envvar="APP_PORT")] = 8000,
    *,
    reload: Annotated[bool, typer.Option(help="Enable hot-reload")] = False,
) -> None:
    uvicorn.run("app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    typer.run(main)
