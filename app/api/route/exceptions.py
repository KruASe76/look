import logfire
from fastapi import FastAPI, Request, Response
from pydantic_core import to_json

from app.core.exceptions import AppError


async def _app_exception_handler(request: Request, exc: AppError) -> Response:
    logfire.exception(
        "Exception raised while handling request",
        request=request,
        _exc_info=exc,
    )

    return Response(
        status_code=exc.status_code,
        content=to_json({"message": exc.message}),
        headers=exc.headers,
        media_type="application/json",
    )


def register_exception_handlers(app: FastAPI) -> None:
    # noinspection PyTypeChecker
    app.add_exception_handler(AppError, _app_exception_handler)
