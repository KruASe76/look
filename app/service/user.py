import logfire
from sqlalchemy.orm import load_only, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model import (
    AuthenticatedUser,
    AuthenticatedUserWithCollectionIds,
    CollectionCreate,
    User,
    UserCartLink,
    UserCreate,
)

from ..core.config import DEFAULT_COLLECTION_NAME
from .collection import CollectionService


# noinspection PyTypeChecker,Pydantic
class UserService:
    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_or_create(session: AsyncSession, user_create: UserCreate) -> User:
        if user_create.telegram_id is not None:
            statement = (
                select(User)
                .where(User.telegram_id == user_create.telegram_id)
                .options(
                    selectinload(User.collections),
                    selectinload(User.cart).selectinload(UserCartLink.product),
                )
            )

            user_optional = (await session.exec(statement)).one_or_none()

            if user_optional is not None:
                return user_optional

        new_user = User.model_validate(user_create)

        session.add(new_user)
        await session.flush()
        await session.refresh(new_user)

        # also creating default collection
        await CollectionService.create(
            session,
            owner_id=new_user.id,
            collection_create=CollectionCreate(name=DEFAULT_COLLECTION_NAME),
        )

        return new_user

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
        statement = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.collections),
                selectinload(User.cart).selectinload(UserCartLink.product),
            )
        )

        return (await session.exec(statement)).one_or_none()

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_authenticated(
        session: AsyncSession, telegram_id: int
    ) -> AuthenticatedUser | None:
        statement = select(User.id).where(User.telegram_id == telegram_id)

        user_id_optional = (await session.exec(statement)).one_or_none()

        if user_id_optional is None:
            return None

        return AuthenticatedUser(id=user_id_optional, telegram_id=telegram_id)

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_authenticated_with_collection_ids(
        session: AsyncSession, telegram_id: int
    ) -> AuthenticatedUserWithCollectionIds | None:
        statement = (
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(load_only(User.id), selectinload(User.collections))
        )

        user = (await session.exec(statement)).one_or_none()

        if user is None:
            return None

        return AuthenticatedUserWithCollectionIds(
            id=user.id,
            telegram_id=telegram_id,
            collection_ids={collection.id for collection in user.collections},
        )
