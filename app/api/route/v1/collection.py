from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.model import BriefCollectionSchema, CollectionCreate, CollectionSchema
from app.service import CollectionService

from .. import messages
from ..dependencies import (
    DatabaseSession,
    DatabaseTransaction,
    InitDataUser,
    InitDataUserWithCollectionIds,
)
from ..util import build_responses

collection_router = APIRouter(prefix="", tags=["collections"])

_responses_with_forbidden = build_responses(
    {status.HTTP_403_FORBIDDEN: messages.COLLECTIONS_FORBIDDEN}, include_auth=True
)


@collection_router.get(
    "/collection/{collection_id}",
    response_model=CollectionSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses(
        {status.HTTP_404_NOT_FOUND: messages.COLLECTION_NOT_FOUND}, include_auth=True
    ),
)
async def get_collection(collection_id: UUID, session: DatabaseSession) -> ...:
    collection_optional = await CollectionService.get_by_id(session, collection_id)

    if collection_optional is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.COLLECTION_NOT_FOUND.format(collection_id),
        )

    return collection_optional


@collection_router.post(
    "/collection",
    response_model=BriefCollectionSchema,
    status_code=status.HTTP_201_CREATED,
    responses=build_responses(include_auth=True),
    description="Create a collection",
)
async def create_collection(
    collection_create: CollectionCreate, user: InitDataUser, session: DatabaseSession
) -> ...:
    return await CollectionService.create(session, user, collection_create)


@collection_router.delete(
    "/collections",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_responses_with_forbidden,
    description="Delete multiple collections",
)
async def delete_collections(
    collection_ids: list[UUID],
    user: InitDataUserWithCollectionIds,
    session: DatabaseSession,
) -> None:
    await CollectionService.delete_bulk(session, user, collection_ids)


@collection_router.post(
    "/collection/products",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_responses_with_forbidden,
    description="Add products to multiple collections",
)
async def add_products_to_collections(
    collection_ids: list[UUID],
    product_ids: list[UUID],
    user: InitDataUserWithCollectionIds,
    session: DatabaseSession,
) -> None:
    await CollectionService.add_products(session, user, collection_ids, product_ids)


@collection_router.delete(
    "/collection/products",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_responses_with_forbidden,
    description="Delete products from multiple collections",
)
async def delete_products_from_collections(
    collection_ids: list[UUID],
    product_ids: list[UUID],
    user: InitDataUserWithCollectionIds,
    session: DatabaseSession,
) -> None:
    await CollectionService.delete_products(session, user, collection_ids, product_ids)


@collection_router.get(
    "/product/{product_id}/collections",
    response_model=list[UUID],
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    description="Get collections that include this product for current user",
)
async def check_product_in_collections(
    product_id: UUID, user: InitDataUserWithCollectionIds, session: DatabaseSession
) -> ...:
    return await CollectionService.check_product_inclusion(session, product_id, user)


@collection_router.put(
    "/product/{product_id}/collections",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=build_responses(include_auth=True),
    description="Update collections that include this product for current user",
)
async def update_product_in_collections(
    product_id: UUID,
    collection_ids: list[UUID],
    user: InitDataUserWithCollectionIds,
    session: DatabaseTransaction,
) -> None:
    await CollectionService.update_collection_inclusion(
        session, product_id, user, collection_ids
    )
