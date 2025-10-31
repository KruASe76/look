from collections.abc import Sequence
from typing import ClassVar
from uuid import UUID

import logfire
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Defaults
from app.core.exceptions import CollectionForbiddenError, CollectionNotFoundError
from app.model import (
    AuthenticatedUserWithCollectionIds,
    Collection,
    CollectionCreate,
    CollectionPatch,
    CollectionProductLink,
    Product,
)

from .util import check_update_needed


# noinspection PyTypeChecker,PyUnresolvedReferences,Pydantic
class CollectionService:
    _default_collection_cache: ClassVar[dict[int, UUID]] = {}
    _DEFAULT_CACHE_MAX_SIZE = 2048

    @staticmethod
    @logfire.instrument(record_return=True)
    async def create(
        session: AsyncSession, owner_id: int, collection_create: CollectionCreate
    ) -> Collection:
        new_collection = Collection.model_validate(collection_create, update={"owner_id": owner_id})

        session.add(new_collection)
        await session.flush()
        await session.refresh(new_collection)

        return new_collection

    @classmethod
    @logfire.instrument(record_return=True)
    async def get_by_id(
        cls,
        session: AsyncSession,
        user_id: int,
        collection_id: UUID,
        *,
        select_products: bool = True,
        select_owner: bool = True,
    ) -> Collection:
        options = []
        if select_products:
            options.append(selectinload(Collection.products))
        if select_owner:
            options.append(joinedload(Collection.owner))

        statement = (
            select(Collection)
            .where(Collection.id == collection_id)
            .options(*options)
        )  # fmt: skip

        try:
            collection = (await session.exec(statement)).one()
        except InvalidRequestError as e:
            raise CollectionNotFoundError from e

        if select_products:
            if collection.owner_id == user_id:
                for product in collection.products:
                    product.is_contained_in_user_collections = True
            else:
                await cls.fill_product_inclusion(
                    session=session, products=collection.products, user_id=user_id
                )

        return collection

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_all_by_owner_id(session: AsyncSession, owner_id: int) -> Sequence[Collection]:
        statement = (
            select(Collection)
            .where(
                Collection.owner_id == owner_id,
                Collection.name != Defaults.collection_name,
            )
            .order_by(Collection.created_at.desc())
        )

        return (await session.exec(statement)).all()

    @classmethod
    @logfire.instrument(record_return=True)
    async def patch(
        cls,
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        collection_id: UUID,
        collection_patch: CollectionPatch,
    ) -> Collection:
        if collection_id not in user.collection_ids:
            raise CollectionForbiddenError

        collection = await cls.get_by_id(
            session=session,
            user_id=user.id,
            collection_id=collection_id,
            select_products=False,
            select_owner=False,
        )

        if check_update_needed(collection_patch, collection):
            collection.sqlmodel_update(collection_patch.model_dump(exclude_unset=True))
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
            raise CollectionForbiddenError

        statement = delete(Collection).where(Collection.id.in_(collection_ids))

        await session.exec(statement)

    @classmethod
    @logfire.instrument(record_return=True)
    async def add_products(
        cls,
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        collection_ids: list[UUID],
        product_ids: list[UUID],
    ) -> None:
        if not collection_ids:
            collection_ids = [
                await cls._get_default_collection_id(session=session, user_id=user.id)
            ]

        if set(collection_ids) - user.collection_ids:
            raise CollectionForbiddenError

        links_to_insert = [
            {"collection_id": c_id, "product_id": p_id}
            for c_id in collection_ids
            for p_id in product_ids
        ]
        if not links_to_insert:
            return

        statement = insert(CollectionProductLink).values(links_to_insert)
        statement = statement.on_conflict_do_nothing(
            index_elements=[CollectionProductLink.collection_id, CollectionProductLink.product_id]
        )
        await session.exec(statement)

    @classmethod
    @logfire.instrument(record_return=True)
    async def delete_products(
        cls,
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        collection_ids: list[UUID],
        product_ids: list[UUID],
    ) -> None:
        if not collection_ids:
            collection_ids = [
                await cls._get_default_collection_id(session=session, user_id=user.id)
            ]

        if set(collection_ids) - user.collection_ids:
            raise CollectionForbiddenError

        statement = delete(CollectionProductLink).where(
            CollectionProductLink.collection_id.in_(collection_ids),
            CollectionProductLink.product_id.in_(product_ids),
        )

        await session.exec(statement)

    @staticmethod
    @logfire.instrument(record_return=True)
    async def check_product_inclusion(
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        product_id: UUID,
    ) -> Sequence[UUID]:
        """:return: list of collection IDs that include given product"""
        if not user.collection_ids:
            return []

        statement = select(CollectionProductLink.collection_id).where(
            CollectionProductLink.product_id == product_id,
            CollectionProductLink.collection_id.in_(user.collection_ids),
        )
        return (await session.exec(statement)).all()

    @classmethod
    @logfire.instrument(record_return=True)
    async def update_product_inclusion(
        cls,
        session: AsyncSession,
        user: AuthenticatedUserWithCollectionIds,
        product_id: UUID,
        new_collection_ids: list[UUID],
    ) -> None:
        """Set the exact list of collections that include the given product (for given user)."""
        if set(new_collection_ids) - user.collection_ids:
            raise CollectionForbiddenError

        current_collection_ids = await cls.check_product_inclusion(
            session=session, user=user, product_id=product_id
        )

        collections_to_add = list(set(new_collection_ids) - set(current_collection_ids))
        collections_to_remove = list(set(current_collection_ids) - set(new_collection_ids))

        if collections_to_add:
            await cls.add_products(
                session=session,
                user=user,
                collection_ids=collections_to_add,
                product_ids=[product_id],
            )

        if collections_to_remove:
            await cls.delete_products(
                session=session,
                user=user,
                collection_ids=collections_to_remove,
                product_ids=[product_id],
            )

    @classmethod
    @logfire.instrument(record_return=True)
    async def fill_product_inclusion(
        cls, session: AsyncSession, products: list[Product], user_id: int
    ) -> None:
        """
        Fill `is_contained_in_user_collections` flag for each product in the list.

        :return: original list with filled flags
        """
        if not products:
            return

        default_collection_id = await cls._get_default_collection_id(
            session=session, user_id=user_id
        )

        statement = select(CollectionProductLink.product_id).where(
            CollectionProductLink.collection_id == default_collection_id,
            CollectionProductLink.product_id.in_([p.id for p in products]),
        )
        product_ids_in_collection = set((await session.exec(statement)).all())

        for product in products:
            product.is_contained_in_user_collections = product.id in product_ids_in_collection

    @classmethod
    @logfire.instrument(record_return=True)
    async def _get_default_collection_id(cls, session: AsyncSession, user_id: int) -> UUID:
        if user_id in cls._default_collection_cache:
            return cls._default_collection_cache[user_id]

        statement = (
            select(Collection.id)
            .where(Collection.owner_id == user_id)
            .order_by(Collection.created_at.asc())
            .limit(1)
        )
        result = (await session.exec(statement)).one_or_none()

        if result is None:
            raise CollectionNotFoundError

        if len(cls._default_collection_cache) >= cls._DEFAULT_CACHE_MAX_SIZE:
            cls._default_collection_cache.pop(next(iter(cls._default_collection_cache)))

        cls._default_collection_cache[user_id] = result
        return result
