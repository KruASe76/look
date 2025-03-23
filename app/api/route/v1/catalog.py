from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.route.dependencies import DatabaseSession, JWTUserId, Pagination
from app.model import BriefProductSchema, ProductSchema
from app.service import CatalogService

catalog_router = APIRouter(prefix="/catalog", tags=["catalog"])


@catalog_router.get(
    "/feed", response_model=list[BriefProductSchema], status_code=status.HTTP_200_OK
)
async def feed(
    pagination: Pagination, user_id: JWTUserId, session: DatabaseSession
) -> ...:
    return await CatalogService.get_feed(
        session, user_id, pagination.limit, pagination.offset
    )


@catalog_router.get(
    "/product/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: UUID, session: DatabaseSession) -> ...:
    product_optional = await CatalogService.get(session, product_id)

    if not product_optional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such product"
        )

    return product_optional
