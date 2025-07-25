import logfire
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import load_only, selectinload
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Defaults
from app.core.exceptions import UserNotFoundException
from app.model import (
    AuthenticatedUser,
    AuthenticatedUserWithCollectionIds,
    CollectionCreate,
    User,
    UserCartLink,
    UserCreate,
    UserPatch,
)

from .collection import CollectionService
from .util import check_update_needed


# noinspection PyTypeChecker,Pydantic
class UserService:
    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_or_upsert(session: AsyncSession, user_create: UserCreate) -> User:
        if user_create.telegram_id is not None:
            statement = (
                select(User)
                .where(User.telegram_id == user_create.telegram_id)
                .options(
                    selectinload(User.collections),
                    selectinload(User.cart).selectinload(UserCartLink.product),
                )
            )

            user_optional: User | None = (await session.exec(statement)).one_or_none()

            if user_optional is not None:
                if check_update_needed(user_create, user_optional):
                    user_optional.sqlmodel_update(
                        user_create.model_dump(exclude_unset=True)
                    )
                    session.add(user_optional)
                    await session.flush()

                return user_optional

        new_user = User.model_validate(user_create)

        session.add(new_user)
        await session.flush()
        await session.refresh(new_user)

        # also creating default collection
        await CollectionService.create(
            session,
            owner_id=new_user.id,
            collection_create=CollectionCreate(
                name=Defaults.collection_name,
                cover_image_url=Defaults.collection_cover_image_url,
            ),
        )
        await session.refresh(new_user, ["collections"])

        return new_user

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_by_id(session: AsyncSession, user_id: int) -> User:
        statement = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.collections),
                selectinload(User.cart).selectinload(UserCartLink.product),
            )
        )

        try:
            return (await session.exec(statement)).one()
        except InvalidRequestError as e:
            raise UserNotFoundException from e

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

    @staticmethod
    @logfire.instrument(record_return=True)
    async def patch(session: AsyncSession, user: User, user_patch: UserPatch) -> User:
        if check_update_needed(user_patch, user):
            user.sqlmodel_update(user_patch.model_dump(exclude_unset=True))
            session.add(user)
            await session.flush()

        return user

    @staticmethod
    @logfire.instrument(record_return=True)
    async def delete_by_id(session: AsyncSession, user_id: int) -> None:
        statement = delete(User).where(User.id == user_id)

        await session.exec(statement)
