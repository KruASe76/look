from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import random
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.catalog import Product


class CatalogService:
    # noinspection PyTypeChecker
    @staticmethod
    async def get(session: AsyncSession, product_id: UUID) -> Product | None:
        statement = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.reviews))
        )

        return (await session.exec(statement)).one_or_none()

    @staticmethod
    async def get_feed(
        session: AsyncSession, user_id: int, limit: int, offset: int  # noqa: ARG004 FIXME
    ) -> Sequence[Product]:
        statement = select(Product).order_by(random()).limit(limit).offset(offset)

        return (await session.exec(statement)).all()
