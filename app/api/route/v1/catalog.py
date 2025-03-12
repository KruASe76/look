from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import random
from sqlmodel import select

from app.api.route.util.dependencies import DatabaseSession, Pagination
from app.model.catalog import BriefProductSchema, Product, ProductSchema

catalog_router = APIRouter(prefix="/catalog", tags=["catalog"])


@catalog_router.get(
    "/feed", response_model=list[BriefProductSchema], status_code=status.HTTP_200_OK
)
async def feed(pagination: Pagination, session: DatabaseSession) -> ...:
    statement = (
        select(Product)
        .order_by(random())
        .limit(pagination.limit)
        .offset(pagination.offset)
    )

    return (await session.exec(statement)).all()


@catalog_router.get(
    "/product/{product_id}",
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: UUID, session: DatabaseSession) -> ...:
    # noinspection PyTypeChecker
    statement = (
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.reviews))
    )

    product_optional: Product | None = (await session.exec(statement)).one_or_none()

    if not product_optional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such product"
        )

    return product_optional
