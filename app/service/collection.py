from uuid import UUID

import logfire
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import (
    CollectionForbiddenException,
    CollectionNotFoundException,
)
from app.model import (
    AuthenticatedUserWithCollectionIds,
    Collection,
    CollectionCreate,
    CollectionPatch,
    CollectionProductLink,
)

from .util import check_update_needed


# noinspection PyTypeChecker,PyUnresolvedReferences,Pydantic
class CollectionService:
    @staticmethod
    @logfire.instrument(record_return=True)
    async def create(
        session: AsyncSession, owner_id: int, collection_create: CollectionCreate
    ) -> Collection:
        new_collection = Collection.model_validate(
            collection_create, update={"owner_id": owner_id}
        )

        session.add(new_collection)
        await session.flush()
        await session.refresh(new_collection)

        return new_collection

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_by_id(session: AsyncSession, collection_id: UUID) -> Collection:
        statement = (
            select(Collection)
            .where(Collection.id == collection_id)
            .options(joinedload(Collection.owner), selectinload(Collection.products))
        )

        try:
            return (await session.exec(statement)).one()
        except InvalidRequestError as e:
            raise CollectionNotFoundException from e

    @staticmethod
    @logfire.instrument(record_return=True)
    async def patch(
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        collection_id: UUID,
        collection_patch: CollectionPatch,
    ) -> Collection:
        if collection_id not in user.collection_ids:
            raise CollectionForbiddenException

        collection = await CollectionService.get_by_id(session, collection_id)

        if check_update_needed(collection_patch, collection):
            collection.sqlmodel_update(
                collection_patch.model_dump(exclude_unset=True)
            )
            session.add(collection)
            await session.flush()

        return collection

    @staticmethod
    @logfire.instrument(record_return=True)
    async def delete_bulk(
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        collection_ids: list[UUID],
    ) -> None:
        if set(collection_ids) - user.collection_ids:
            raise CollectionForbiddenException

        statement = delete(Collection).where(Collection.id.in_(collection_ids))

        await session.exec(statement)

    @staticmethod
    @logfire.instrument(record_return=True)
    async def add_products(
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        collection_ids: list[UUID],
        product_ids: list[UUID],
    ) -> None:
        if set(collection_ids) - user.collection_ids:
            raise CollectionForbiddenException

        links_to_insert = [
            {"collection_id": c_id, "product_id": p_id}
            for c_id in collection_ids
            for p_id in product_ids
        ]
        if not links_to_insert:
            return

        statement = insert(CollectionProductLink).values(links_to_insert)
        statement = statement.on_conflict_do_nothing(
            index_elements=[
                CollectionProductLink.collection_id,
                CollectionProductLink.product_id,
            ]
        )
        await session.exec(statement)

    @staticmethod
    @logfire.instrument(record_return=True)
    async def delete_products(
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        collection_ids: list[UUID],
        product_ids: list[UUID],
    ) -> None:
        if set(collection_ids) - user.collection_ids:
            raise CollectionForbiddenException

        statement = delete(CollectionProductLink).where(
            CollectionProductLink.collection_id.in_(collection_ids),
            CollectionProductLink.product_id.in_(product_ids),
        )

        await session.exec(statement)

    @staticmethod
    @logfire.instrument(record_return=True)
    async def check_product_inclusion(
        session: AsyncSession,
        product_id: UUID,
        user: AuthenticatedUserWithCollectionIds,
    ) -> list[UUID]:
        if not user.collection_ids:
            return []

        statement = select(CollectionProductLink.collection_id).where(
            CollectionProductLink.product_id == product_id,
            CollectionProductLink.collection_id.in_(user.collection_ids),
        )
        return (await session.exec(statement)).scalars().all()

    @staticmethod
    @logfire.instrument(record_return=True)
    async def update_collection_inclusion(
        session: AsyncSession,
        product_id: UUID,
        user: AuthenticatedUserWithCollectionIds,
        new_collection_ids: list[UUID],
    ) -> None:
        if set(new_collection_ids) - user.collection_ids:
            raise CollectionForbiddenException

        current_collection_ids = await CollectionService.check_product_inclusion(
            session, product_id, user
        )

        collections_to_add = list(set(new_collection_ids) - set(current_collection_ids))
        collections_to_remove = list(
            set(current_collection_ids) - set(new_collection_ids)
        )

        if collections_to_add:
            await CollectionService.add_products(
                session, user, collections_to_add, [product_id]
            )

        if collections_to_remove:
            await CollectionService.delete_products(
                session, user, collections_to_remove, [product_id]
            )
