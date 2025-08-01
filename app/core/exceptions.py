from typing import ClassVar

from fastapi import status

from app.core.config import INIT_DATA_SCHEME_NAME


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Unknown error"
    headers: ClassVar[dict[str, str] | None] = None


class UnauthorizedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized"


class InitDataUnauthorizedException(UnauthorizedException):
    message = f"{INIT_DATA_SCHEME_NAME} init-data missing"
    headers: ClassVar = {
        "WWW-Authenticate": f'{INIT_DATA_SCHEME_NAME} realm="authentication", error="missing"'
    }


class ApiKeyUnauthorizedException(UnauthorizedException):
    message = "API key missing"
    headers: ClassVar = {
        "WWW-Authenticate": 'ApiKey realm="internal authentication", error="missing"'
    }


class ForbiddenException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Forbidden"


class InitDataForbiddenException(ForbiddenException):
    message = f"{INIT_DATA_SCHEME_NAME} init-data invalid or expired"


class ApiKeyForbiddenException(ForbiddenException):
    message = "API key invalid"


class CollectionForbiddenException(ForbiddenException):
    message = "User has no permission to edit one of the collections"


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Not found"


class UserNotFoundException(NotFoundException):
    message = "User not found"


class ProductNotFoundException(NotFoundException):
    message = "Product not found"


class CollectionNotFoundException(NotFoundException):
    message = "Collection not found"
