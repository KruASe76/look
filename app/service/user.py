from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model import User, UserCartLink, UserCreate


class UserService:
    # noinspection PyTypeChecker
    @staticmethod
    async def get_or_create(user_create: UserCreate, session: AsyncSession) -> User:
        if user_create.telegram_id is not None:
            select_statement = (
                select(User)
                .where(User.telegram_id == user_create.telegram_id)
                .options(
                    selectinload(User.cart).selectinload(UserCartLink.product)
                )  # FIXME: add collections
            )

            user_optional = (await session.exec(select_statement)).one_or_none()

            if user_optional is not None:
                return user_optional

        new_user = User.model_validate(user_create)

        session.add(new_user)
        await session.flush()
        await session.refresh(new_user)

        return new_user
