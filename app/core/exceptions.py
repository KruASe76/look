from typing import ClassVar

from fastapi import status

from app.core.config import INIT_DATA_SCHEME_NAME


class AppError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Unknown error"
    headers: ClassVar[dict[str, str] | None] = None


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized"


class InitDataUnauthorizedError(UnauthorizedError):
    message = f"{INIT_DATA_SCHEME_NAME} init-data missing"
    headers: ClassVar = {
        "WWW-Authenticate": f'{INIT_DATA_SCHEME_NAME} realm="authentication", error="missing"'
    }


class ApiKeyUnauthorizedError(UnauthorizedError):
    message = "API key missing"
    headers: ClassVar = {
        "WWW-Authenticate": 'ApiKey realm="internal authentication", error="missing"'
    }


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Forbidden"


class InitDataForbiddenError(ForbiddenError):
    message = f"{INIT_DATA_SCHEME_NAME} init-data invalid or expired"


class ApiKeyForbiddenError(ForbiddenError):
    message = "API key invalid"


class CollectionForbiddenError(ForbiddenError):
    message = "User has no permission to edit one of the collections"


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Not found"


class UserNotFoundError(NotFoundError):
    message = "User not found"


class ProductNotFoundError(NotFoundError):
    message = "Product not found"


class CollectionNotFoundError(NotFoundError):
    message = "Collection not found"
