from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, status

from app.model import SearchMeta
from app.service import SearchService

from ..auth import DevAPIKey
from ..dependencies import DatabaseSession
from ..util import build_responses

dev_router = APIRouter(prefix="/dev", tags=["dev"], dependencies=[DevAPIKey])

dev_responses = build_responses(include_dev_auth=True)


@dev_router.post(
    "/search/sync",
    response_model=int,
    status_code=status.HTTP_201_CREATED,
    responses=dev_responses,
    summary="Sync search index with database, return number of products synced",
)
async def sync_search(
    since: Annotated[datetime, Body(embed=True)], session: DatabaseSession
) -> ...:
    return await SearchService.sync_products(session, since)


@dev_router.post(
    "/search/meta/refresh-cache",
    response_model=SearchMeta,
    status_code=status.HTTP_201_CREATED,
    responses=dev_responses,
    summary="Refresh search metadata cache, return fresh metadata",
)
async def refresh_search_meta(session: DatabaseSession) -> ...:
    return await SearchService.refresh_meta_cache(session)
