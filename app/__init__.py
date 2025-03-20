__all__ = ["main"]

import uvicorn

from .api import app


def main() -> None:
    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104
        port=8000,
    )
