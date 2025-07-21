from fastapi import APIRouter, status

from app.core.config import BRANDS_USER_ID, TRENDS_USER_ID
from app.model import CollectionSchema
from app.service import CollectionService

from ..dependencies import DatabaseSession

feature_router = APIRouter(prefix="/feature", tags=["feature"])


@feature_router.get(
    "/trends",
    response_model=list[CollectionSchema],
    status_code=status.HTTP_200_OK,
    summary="Get trends collections",
)
async def get_trends(session: DatabaseSession) -> ...:
    return await CollectionService.get_by_owner_id(session, TRENDS_USER_ID)


@feature_router.get(
    "/brands",
    response_model=list[CollectionSchema],
    status_code=status.HTTP_200_OK,
    summary="Get brands collections",
)
async def get_brands(session: DatabaseSession) -> ...:
    return await CollectionService.get_by_owner_id(session, BRANDS_USER_ID)
