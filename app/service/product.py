from collections.abc import Sequence
from uuid import UUID

import logfire
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import ProductNotFoundError
from app.model import Product


# noinspection PyTypeChecker,Pydantic
class ProductService:
    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_by_id(session: AsyncSession, product_id: UUID) -> Product:
        statement = (  # assuming full load
            select(Product)
            .where(Product.id == product_id)
            .options(joinedload(Product.color_group))
        )  # fmt: skip

        try:
            return (await session.exec(statement)).unique().one()
        except InvalidRequestError as e:
            raise ProductNotFoundError from e

    # noinspection PyUnresolvedReferences
    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_many_by_ids(session: AsyncSession, product_ids: Sequence[UUID]) -> list[Product]:
        if not product_ids:
            return []

        statement = (  # assuming brief load
            select(Product).where(Product.id.in_(product_ids))
        )

        return (await session.exec(statement)).all()
