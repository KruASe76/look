from fastapi.security import APIKeyHeader
from fastapi.security.http import HTTPBase

from app.core.config import INIT_DATA_DESCRIPTION, INIT_DATA_SCHEME_NAME


class AuthConfig:
    init_data_scheme = HTTPBase(
        scheme=INIT_DATA_SCHEME_NAME,
        description=INIT_DATA_DESCRIPTION,
        auto_error=False,
    )

    api_key_scheme = APIKeyHeader(name="x-api-key")
