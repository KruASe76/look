import logfire
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse

from app.core.exceptions import AppException


async def _app_exception_handler(request: Request, exc: AppException) -> Response:
    logfire.exception(
        "Exception raised while handling request", request=request, _exc_info=exc
    )

    return ORJSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
        headers=exc.headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    # noinspection PyTypeChecker
    app.add_exception_handler(AppException, _app_exception_handler)
