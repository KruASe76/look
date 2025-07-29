from uuid import UUID

import logfire
from fastapi import APIRouter, status

from app.api.schema import SearchQuery, SearchSuggestionQuery
from app.core.exceptions import ProductNotFoundException
from app.model import BriefProductSchema, ProductSchema, SearchMeta
from app.service import CatalogService, CollectionService, SearchService

from ..auth import InitDataUser
from ..dependencies import DatabaseSession, DatabaseTransaction, Pagination
from ..util import build_responses

catalog_router = APIRouter(prefix="/catalog", tags=["catalog"])


@catalog_router.get(
    "/product/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses(ProductNotFoundException),
    summary="Get product by id",
)
async def get_product(
    product_id: UUID, user: InitDataUser, session: DatabaseTransaction
) -> ...:
    product = await CatalogService.get_by_id(session, product_id)
    await CollectionService.fill_inclusion(session, [product], user.id)

    return product


@catalog_router.post(
    "/search",
    response_model=list[BriefProductSchema],
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    summary="Search products",
)
async def search_catalog(
    query: SearchQuery,
    pagination: Pagination,
    user: InitDataUser,
    session: DatabaseTransaction,
) -> ...:
    product_ids = await SearchService.search_products(
        user_id=user.id,
        query=query.query,
        categories=query.categories,
        colors=query.colors,
        brands=query.brands,
        sizes=query.sizes,
        min_price=query.min_price,
        max_price=query.max_price,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    products = await CatalogService.get_by_ids(session, product_ids)
    await CollectionService.fill_inclusion(session, products, user.id)

    logfire.info("why", product_ids=product_ids, products=products)
    return products


@catalog_router.post(
    "/search/suggestions",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    summary="Get search suggestions",
)
async def search_suggestions(query: SearchSuggestionQuery) -> ...:
    return await SearchService.get_suggestions(query.query, query.limit)


@catalog_router.get(
    "/search/meta",
    response_model=SearchMeta,
    status_code=status.HTTP_200_OK,
    summary="Get search metadata",
)
async def get_search_meta(session: DatabaseSession) -> ...:
    return await SearchService.get_meta(session)
