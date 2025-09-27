__all__ = [
    "CollectionService",
    "InteractionService",
    "ProductService",
    "SearchService",
    "UserService",
    "warmup",
]

from contextlib import asynccontextmanager

from .collection import CollectionService
from .interaction import InteractionService
from .product import ProductService
from .search import SearchService
from .user import UserService


async def warmup() -> None:
    from app.database import spawn_session

    async with asynccontextmanager(spawn_session)() as session:
        await SearchService.refresh_meta_cache(session=session)
