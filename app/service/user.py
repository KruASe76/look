from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model import User, UserCartLink


class UserService:
    # noinspection PyTypeChecker
    @staticmethod
    async def create_user(
        telegram_id: int | None,
        username: str | None,
        first_name: str,
        last_name: str | None,
        session: AsyncSession,
    ) -> User:
        insert_statement = (
            insert(User)
            .values(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            .on_conflict_do_nothing()
            .returning(User.id)
        )

        user_id = (await session.exec(insert_statement)).scalar_one_or_none()

        select_statement = (
            select(User)
            .where(
                (User.id == user_id) if user_id else (User.telegram_id == telegram_id)
            )
            .options(
                selectinload(User.cart).selectinload(UserCartLink.product)
            )  # FIXME: add collections
        )

        return (await session.exec(select_statement)).one()
