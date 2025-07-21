__all__ = [
    "CatalogService",
    "CollectionService",
    "InteractionService",
    "SearchService",
    "UserService",
    "warmup",
]

from .catalog import CatalogService
from .collection import CollectionService
from .interaction import InteractionService
from .search import SearchService
from .user import UserService


async def warmup() -> None:
    from app.database import spawn_session

    async with spawn_session() as session:
        await SearchService.refresh_meta_cache(session)
