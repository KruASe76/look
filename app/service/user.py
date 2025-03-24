from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model import User, UserCartLink, UserCreate


class UserService:
    # noinspection PyTypeChecker
    @staticmethod
    async def create_user(user_create: UserCreate, session: AsyncSession) -> User:
        insert_statement = (
            insert(User)
            .values(**user_create.model_dump())
            .on_conflict_do_nothing()
            .returning(User.id)
        )

        user_id = (await session.exec(insert_statement)).scalar_one_or_none()

        select_statement = (
            select(User)
            .where(
                (User.id == user_id)
                if user_id
                else (User.telegram_id == user_create.telegram_id)
            )
            .options(
                selectinload(User.cart).selectinload(UserCartLink.product)
            )  # FIXME: add collections
        )

        return (await session.exec(select_statement)).one()
