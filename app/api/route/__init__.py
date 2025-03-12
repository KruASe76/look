__all__ = ["root_router"]

from fastapi import APIRouter
from starlette.responses import RedirectResponse

from .v1 import v1_router

root_router = APIRouter()

root_router.include_router(v1_router)


@root_router.get("/", include_in_schema=False, response_model=None)
async def docs_redirect() -> ...:
    return RedirectResponse(url="/docs")
