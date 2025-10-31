from functools import cache

from pydantic import create_model

from app.core.exceptions import (
    ApiKeyForbiddenError,
    ApiKeyUnauthorizedError,
    AppError,
    InitDataForbiddenError,
    InitDataUnauthorizedError,
)


@cache
def _build_responses_internal(exceptions: tuple[type[AppError]]) -> dict[int, dict[str, ...]]:
    return {
        exception.status_code: {
            "model": create_model(
                exception.__name__,
                message=(str, exception.message),
            )
        }
        for exception in exceptions
    }


@cache
def build_responses(
    *exceptions: type[AppError],
    include_auth: bool = False,
    include_dev_auth: bool = False,
) -> dict[int, dict[str, ...]]:
    exception_list: list[type[AppError]] = []

    if include_auth:
        exception_list.extend((InitDataUnauthorizedError, InitDataForbiddenError))
    if include_dev_auth:
        exception_list.extend((ApiKeyForbiddenError, ApiKeyUnauthorizedError))

    exception_list.extend(exceptions)

    return _build_responses_internal(tuple(exception_list))
