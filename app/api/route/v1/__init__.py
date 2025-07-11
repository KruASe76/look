__all__ = ["v1_router"]

from fastapi import APIRouter

from .auth import auth_router
from .catalog import catalog_router
from .collection import collection_router
from .user import user_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)
v1_router.include_router(catalog_router)
v1_router.include_router(user_router)
v1_router.include_router(collection_router)
