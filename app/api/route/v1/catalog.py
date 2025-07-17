from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.schema import SearchQuery
from app.model import BriefProductSchema, ProductSchema
from app.service import CatalogService, SearchService

from .. import messages
from ..dependencies import DatabaseSession, InitDataUser, Pagination
from ..util import build_responses

catalog_router = APIRouter(prefix="/catalog", tags=["catalog"])


@catalog_router.get(
    "/product/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses({status.HTTP_404_NOT_FOUND: messages.PRODUCT_NOT_FOUND}),
    description="Get product by id",
)
async def get_product(product_id: UUID, session: DatabaseSession) -> ...:
    product_optional = await CatalogService.get_by_id(session, product_id)

    if not product_optional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PRODUCT_NOT_FOUND
        )

    return product_optional


@catalog_router.get(
    "/feed",
    response_model=list[BriefProductSchema],
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    description="Get feed of products",
)
async def feed(
    pagination: Pagination, user: InitDataUser, session: DatabaseSession
) -> ...:
    return await CatalogService.get_feed(
        session, user, pagination.limit, pagination.offset
    )


@catalog_router.post(
    "/search",
    response_model=list[BriefProductSchema],
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    description="Search products",
)
async def search_catalog(
    user: InitDataUser,
    query: SearchQuery,
    pagination: Pagination,
    session: DatabaseSession,
) -> ...:
    product_ids = await SearchService.search_products(
        user=user,
        query=query.query,
        categories=query.categories,
        colors=query.colors,
        brands=query.brands,
        min_price=query.min_price,
        max_price=query.max_price,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    return await CatalogService.get_by_ids(session, product_ids)
