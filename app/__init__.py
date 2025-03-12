__all__ = ["main"]

from pathlib import Path

import uvicorn

from .api import app

cert_path = Path("certs/cert.pem")
key_path = Path("certs/key.pem")


def main() -> None:
    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104
        port=8000,
        ssl_certfile=cert_path,
        ssl_keyfile=key_path,
    )
