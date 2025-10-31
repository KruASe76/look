from uuid import UUID

import logfire
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import ProductNotFoundError
from app.model import Interaction, InteractionType


# noinspection PyTypeChecker
class InteractionService:
    @staticmethod
    @logfire.instrument(record_return=True)
    async def record_product_interaction(
        session: AsyncSession,
        user_id: int,
        product_id: UUID,
        interaction_type: InteractionType,
    ) -> None:
        statement = (
            insert(Interaction)
            .values(
                user_id=user_id,
                product_id=product_id,
                interaction_type=interaction_type,
            )
            .on_conflict_do_update(
                index_elements=["user_id", "product_id"],
                set_={"interaction_type": interaction_type},
            )
        )

        try:
            await session.exec(statement)
        except IntegrityError as e:
            raise ProductNotFoundError from e
