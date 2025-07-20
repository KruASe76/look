from typing import Annotated

from fastapi import Depends

from app.core.config import DEV_API_KEY
from app.core.exceptions import ApiKeyForbiddenException, ApiKeyUnauthorizedException

from .config import AuthConfig


async def validate_api_key(
    api_key: Annotated[str | None, Depends(AuthConfig.api_key_scheme)],
) -> None:
    if not api_key:
        raise ApiKeyUnauthorizedException

    if api_key != DEV_API_KEY:
        raise ApiKeyForbiddenException


DevAPIKey = Depends(validate_api_key)
