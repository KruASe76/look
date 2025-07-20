from functools import cache

from pydantic import create_model

from app.core.exceptions import (
    ApiKeyForbiddenException,
    ApiKeyUnauthorizedException,
    AppException,
    InitDataForbiddenException,
    InitDataUnauthorizedException,
)


@cache
def _build_responses_internal(
    exceptions: tuple[type[AppException]],
) -> dict[int, dict[str, ...]]:
    return {
        exception.status_code: {
            "model": create_model(
                exception.__name__.replace("Exception", "Error"),
                message=(str, exception.message),
            )
        }
        for exception in exceptions
    }


@cache
def build_responses(
    *exceptions: type[AppException],
    include_auth: bool = False,
    include_dev_auth: bool = False,
) -> dict[int, dict[str, ...]]:
    exception_list: list[type[AppException]] = []

    if include_auth:
        exception_list.extend(
            (InitDataUnauthorizedException, InitDataForbiddenException)
        )

    if include_dev_auth:
        exception_list.extend((ApiKeyForbiddenException, ApiKeyUnauthorizedException))

    exception_list.extend(exceptions)

    return _build_responses_internal(tuple(exception_list))
