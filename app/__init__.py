__all__ = ["main"]

import os
from pathlib import Path

import logfire
import uvicorn
from logfire import ScrubbingOptions

from .api import app

cert_path = Path("certs/cert.pem")
key_path = Path("certs/key.pem")


def main() -> None:
    logfire.configure(
        service_name=os.getenv("LOGFIRE_SERVICE_NAME"),
        environment=os.getenv("LOGFIRE_ENVIRONMENT"),
        scrubbing=ScrubbingOptions(extra_patterns=["token"]),
    )

    logfire.instrument_pydantic()
    logfire.instrument_fastapi(app)

    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104
        port=8000,
        ssl_certfile=cert_path if cert_path.exists() else None,
        ssl_keyfile=key_path if key_path.exists() else None,
    )
