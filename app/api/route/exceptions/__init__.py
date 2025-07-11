__all__ = ["add_exception_handlers"]

from fastapi import FastAPI

from app.core.exceptions import CollectionForbiddenException

from .handlers import forbidden_exception_handler


# noinspection PyTypeChecker
def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(CollectionForbiddenException, forbidden_exception_handler)
