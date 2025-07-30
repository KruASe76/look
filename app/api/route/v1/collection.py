from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, status

from app.core.exceptions import (
    CollectionForbiddenException,
    CollectionNotFoundException,
)
from app.model import (
    BriefCollectionSchema,
    CollectionCreate,
    CollectionPatch,
    CollectionSchemaWithOwner,
)
from app.service import CollectionService

from ..auth import InitDataUser, InitDataUserWithCollectionIds
from ..dependencies import DatabaseTransaction
from ..util import build_responses

collection_router = APIRouter(prefix="", tags=["collection"])


@collection_router.post(
    "/collection",
    response_model=BriefCollectionSchema,
    status_code=status.HTTP_201_CREATED,
    responses=build_responses(include_auth=True),
    summary="Create a collection",
)
async def create_collection(
    collection_create: CollectionCreate,
    user: InitDataUser,
    session: DatabaseTransaction,
) -> ...:
    return await CollectionService.create(
        session=session, owner_id=user.id, collection_create=collection_create
    )


@collection_router.get(
    "/collection/{collection_id}",
    response_model=CollectionSchemaWithOwner,
    status_code=status.HTTP_200_OK,
    responses=build_responses(CollectionNotFoundException, include_auth=True),
    summary="Get collection by id",
)
async def get_collection(
    collection_id: UUID, user: InitDataUser, session: DatabaseTransaction
) -> ...:
    return await CollectionService.get_by_id(
        session=session, user_id=user.id, collection_id=collection_id
    )


@collection_router.patch(
    "/collection/{collection_id}",
    response_model=BriefCollectionSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses(
        CollectionForbiddenException, CollectionNotFoundException, include_auth=True
    ),
    summary="Partially update collection by id",
)
async def patch_collection(
    collection_id: UUID,
    collection_patch: Annotated[CollectionPatch, Body()],
    user: InitDataUserWithCollectionIds,
    session: DatabaseTransaction,
) -> ...:
    return await CollectionService.patch(
        session=session,
        user=user,
        collection_id=collection_id,
        collection_patch=collection_patch,
    )


@collection_router.delete(
    "/collections",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=build_responses(CollectionForbiddenException, include_auth=True),
    summary="Delete multiple collections",
)
async def delete_collections(
    collection_ids: list[UUID],
    user: InitDataUserWithCollectionIds,
    session: DatabaseTransaction,
) -> None:
    await CollectionService.delete_bulk(
        session=session, user=user, collection_ids=collection_ids
    )


@collection_router.post(
    "/collection/products",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=build_responses(CollectionForbiddenException, include_auth=True),
    summary="Add products to multiple collections",
)
async def add_products_to_collections(
    collection_ids: list[UUID],
    product_ids: list[UUID],
    user: InitDataUserWithCollectionIds,
    session: DatabaseTransaction,
) -> None:
    await CollectionService.add_products(
        session=session,
        user=user,
        collection_ids=collection_ids,
        product_ids=product_ids,
    )


@collection_router.delete(
    "/collection/products",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=build_responses(CollectionForbiddenException, include_auth=True),
    summary="Delete products from multiple collections",
)
async def delete_products_from_collections(
    collection_ids: list[UUID],
    product_ids: list[UUID],
    user: InitDataUserWithCollectionIds,
    session: DatabaseTransaction,
) -> None:
    await CollectionService.delete_products(
        session=session,
        user=user,
        collection_ids=collection_ids,
        product_ids=product_ids,
    )


@collection_router.get(
    "/product/{product_id}/collections",
    response_model=list[UUID],
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    summary="Get collections that include this product for current user",
)
async def check_product_in_collections(
    product_id: UUID, user: InitDataUserWithCollectionIds, session: DatabaseTransaction
) -> ...:
    return await CollectionService.check_product_inclusion(
        session=session, user=user, product_id=product_id
    )


@collection_router.put(
    "/product/{product_id}/collections",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=build_responses(include_auth=True),
    summary="Update collections that include this product for current user",
)
async def update_product_in_collections(
    product_id: UUID,
    collection_ids: list[UUID],
    user: InitDataUserWithCollectionIds,
    session: DatabaseTransaction,
) -> None:
    await CollectionService.update_product_inclusion(
        session=session,
        user=user,
        product_id=product_id,
        new_collection_ids=collection_ids,
    )
