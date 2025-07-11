from fastapi import HTTPException, status
from fastapi.requests import Request

from app.api.route import messages
from app.core.exceptions import CollectionForbiddenException


# noinspection PyUnusedLocal
async def forbidden_exception_handler(
    request: Request,  # noqa: ARG001
    exc: CollectionForbiddenException,  # noqa: ARG001
) -> ...:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail=messages.COLLECTIONS_FORBIDDEN
    )
