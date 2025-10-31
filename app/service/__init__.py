__all__ = [
    "CollectionService",
    "InteractionService",
    "ProductService",
    "SearchService",
    "UserService",
    "listen",
    "warmup",
]

import asyncio

from .collection import CollectionService
from .interaction import InteractionService
from .product import ProductService
from .search import SearchService
from .user import UserService


async def warmup() -> None:
    await SearchService.handle_meta_refresh_notification()


async def listen() -> None:
    await asyncio.gather(
        SearchService.meta_refresh_listener(),
    )
