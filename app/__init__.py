__all__ = ["app"]

import logfire

from app.core.config import LOGFIRE_ENVIRONMENT, LOGFIRE_SERVICE_NAME

from .api import app

logfire.configure(
    service_name=LOGFIRE_SERVICE_NAME,
    environment=LOGFIRE_ENVIRONMENT,
    send_to_logfire="if-token-present",
    distributed_tracing=False,
)

logfire.instrument_pydantic()
logfire.instrument_fastapi(app)
