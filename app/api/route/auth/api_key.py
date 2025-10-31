from typing import Annotated

from fastapi import Depends

from app.core.config import DEV_API_KEY
from app.core.exceptions import ApiKeyForbiddenError, ApiKeyUnauthorizedError

from .config import AuthConfig


async def validate_api_key(
    api_key: Annotated[str | None, Depends(AuthConfig.api_key_scheme)],
) -> None:
    if api_key is None:
        raise ApiKeyUnauthorizedError

    if api_key != DEV_API_KEY:
        raise ApiKeyForbiddenError


DevAPIKey = Depends(validate_api_key)
