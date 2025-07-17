from collections.abc import Sequence
from uuid import UUID

import logfire
from sqlalchemy.sql.functions import random
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model import Product, User


# noinspection PyTypeChecker,Pydantic
class CatalogService:
    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_by_id(session: AsyncSession, product_id: UUID) -> Product | None:
        statement = select(Product).where(Product.id == product_id)

        return (await session.exec(statement)).one_or_none()

    # noinspection PyUnresolvedReferences
    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_by_ids(
        session: AsyncSession, product_ids: list[UUID]
    ) -> Sequence[Product]:
        statement = select(Product).where(Product.id.in_(product_ids))

        return (await session.exec(statement)).all()

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_feed(
        session: AsyncSession,
        user: User,  # noqa: ARG004 TODO
        limit: int,
        offset: int,
    ) -> Sequence[Product]:
        statement = select(Product).order_by(random()).limit(limit).offset(offset)

        return (await session.exec(statement)).all()
