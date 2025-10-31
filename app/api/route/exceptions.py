import logfire
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse

from app.core.exceptions import AppError


async def _app_exception_handler(request: Request, exc: AppError) -> Response:
    logfire.exception(
        "Exception raised while handling request",
        request=request,
        _exc_info=exc,
    )

    return ORJSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
        headers=exc.headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    # noinspection PyTypeChecker
    app.add_exception_handler(AppError, _app_exception_handler)
