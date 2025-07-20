from uuid import UUID

from fastapi import APIRouter, status

from app.api.schema import SearchQuery
from app.core.exceptions import ProductNotFoundException
from app.model import BriefProductSchema, ProductSchema
from app.service import CatalogService, SearchService

from ..auth import InitDataUser
from ..dependencies import DatabaseSession, Pagination
from ..util import build_responses

catalog_router = APIRouter(prefix="/catalog", tags=["catalog"])


@catalog_router.get(
    "/product/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses(ProductNotFoundException),
    summary="Get product by id",
)
async def get_product(product_id: UUID, session: DatabaseSession) -> ...:
    return await CatalogService.get_by_id(session, product_id)


@catalog_router.post(
    "/search",
    response_model=list[BriefProductSchema],
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    summary="Search products",
)
async def search_catalog(
    user: InitDataUser,
    query: SearchQuery,
    pagination: Pagination,
    session: DatabaseSession,
) -> ...:
    product_ids = await SearchService.search_products(
        user=user.id,
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
