import logfire
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model import User, UserCartLink, UserCreate


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
                    selectinload(User.cart).selectinload(UserCartLink.product)
                )  # FIXME: add collections
            )

            user_optional = (await session.exec(statement)).one_or_none()

            if user_optional is not None:
                return user_optional

        new_user = User.model_validate(user_create)

        session.add(new_user)
        await session.flush()
        await session.refresh(new_user)

        return new_user

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
        statement = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.cart).selectinload(UserCartLink.product)
            )  # FIXME: add collections
        )

        return (await session.exec(statement)).one_or_none()
