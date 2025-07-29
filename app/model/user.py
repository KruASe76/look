from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.core.config import Defaults

from .collection import Collection

if TYPE_CHECKING:
    from . import BriefCollectionSchema, BriefProductSchema, Product


# noinspection PyTypeChecker
class _BriefUserBase(SQLModel):
    telegram_id: int | None = Field(unique=True)
    username: str | None = Field(max_length=64, sa_type=String(64))
    first_name: str = Field(max_length=64, sa_type=String(64), nullable=False)
    last_name: str | None = Field(max_length=64, sa_type=String(64))
    photo_url: str | None


class _UserBase(_BriefUserBase):
    preferences: dict[str, Any] = Field(
        sa_column=Column(JSONB, server_default="{}", nullable=False),
        default_factory=dict,
    )


class _UserIdModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


# noinspection PyUnresolvedReferences,Pydantic
class User(_UserBase, _UserIdModel, table=True):
    __tablename__ = "user"

    collections: list["Collection"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={
            "order_by": lambda: (
                (Collection.name == Defaults.collection_name).desc(),
                Collection.created_at.desc(),
            )
        },
    )
    cart: list["UserCartLink"] = Relationship(back_populates="user")


class UserCreate(_UserBase):
    pass


class UserPatch(SQLModel):
    telegram_id: int | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    photo_url: str | None = None

    preferences: dict[str, Any] | None = None


class _UserIdSchema(SQLModel):
    id: int


class BriefUserSchema(_BriefUserBase, _UserIdSchema):
    pass


class UserWithPreferencesSchema(_UserBase, _UserIdSchema):
    pass


class UserSchema(UserWithPreferencesSchema):
    collections: list["BriefCollectionSchema"] = []
    # cart: list["UserCartSchema"] = []  # maybe later


# AUTH


class AuthenticatedUser(SQLModel):
    id: int
    telegram_id: int


class AuthenticatedUserWithCollectionIds(AuthenticatedUser):
    collection_ids: set[UUID]


# CART


class _UserCartBase(SQLModel):
    quantity: int = Field(ge=1, default=1, nullable=False)


class _UserCartIds(SQLModel):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", primary_key=True)
    product_id: UUID = Field(
        foreign_key="product.id", ondelete="CASCADE", primary_key=True
    )


class UserCartLink(_UserCartBase, _UserCartIds, table=True):
    __tablename__ = "user_cart"

    user: User = Relationship(back_populates="cart")
    product: "Product" = Relationship()


class UserCartSchema(_UserCartBase):
    product: "BriefProductSchema"
