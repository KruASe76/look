from enum import StrEnum
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, SQLModel


class InteractionType(StrEnum):
    LIKE = "like"
    DISLIKE = "dislike"


# noinspection PyTypeChecker
class Interaction(SQLModel, table=True):
    __tablename__ = "interaction"

    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", primary_key=True)
    product_id: UUID = Field(
        foreign_key="product.id",
        ondelete="CASCADE",
        primary_key=True,
        sa_type=PG_UUID(as_uuid=True),
    )

    interaction_type: InteractionType = Field(
        sa_type=SAEnum(InteractionType), nullable=False
    )
