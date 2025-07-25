import random

from fastapi import APIRouter, status

from app.core.config import SpecialUserIds
from app.model import BriefCollectionSchema
from app.service import CollectionService

from ..auth import InitDataUser
from ..dependencies import DatabaseSession

feature_router = APIRouter(prefix="/feature", tags=["feature"])


@feature_router.get(
    "/trends/global",
    response_model=list[BriefCollectionSchema],
    status_code=status.HTTP_200_OK,
    summary="Get trends collections",
)
async def get_global_trends(session: DatabaseSession) -> ...:
    return await CollectionService.get_by_owner_id(
        session, SpecialUserIds.GLOBAL_TRENDS
    )


@feature_router.get(
    "/brands/global",
    response_model=list[BriefCollectionSchema],
    status_code=status.HTTP_200_OK,
    summary="Get brands collections",
)
async def get_global_brands(session: DatabaseSession) -> ...:
    return await CollectionService.get_by_owner_id(
        session, SpecialUserIds.GLOBAL_BRANDS
    )


@feature_router.get(
    "/trends/personal",
    response_model=list[BriefCollectionSchema],
    status_code=status.HTTP_200_OK,
    summary="Get trends collections",
)
async def get_personal_trends(user: InitDataUser, session: DatabaseSession) -> ...:  # noqa: ARG001
    result = list(
        await CollectionService.get_by_owner_id(session, SpecialUserIds.PERSONAL_TRENDS)
    )

    random.shuffle(result)

    return result


@feature_router.get(
    "/brands/personal",
    response_model=list[BriefCollectionSchema],
    status_code=status.HTTP_200_OK,
    summary="Get brands collections",
)
async def get_personal_brands(user: InitDataUser, session: DatabaseSession) -> ...:  # noqa: ARG001
    result = list(
        await CollectionService.get_by_owner_id(session, SpecialUserIds.PERSONAL_BRANDS)
    )

    random.shuffle(result)

    return result
