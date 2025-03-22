from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.user import User


class UserService:
    # noinspection PyTypeChecker
    @staticmethod
    async def create_user(user_id: int, session: AsyncSession) -> User:
        insert_statement = insert(User).values(id=user_id).on_conflict_do_nothing()

        await session.exec(insert_statement)

        select_statement = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.cart))  # FIXME: add collections
        )

        return (await session.exec(select_statement)).one()
