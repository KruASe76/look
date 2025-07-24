from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from .misc import UserPreferences

if TYPE_CHECKING:
    from . import BriefCollectionSchema, BriefProductSchema, Collection, Product


# noinspection PyTypeChecker
class BriefUserBase(SQLModel):
    telegram_id: int | None = Field(unique=True)
    username: str | None = Field(max_length=64, sa_type=String(64))
    first_name: str = Field(max_length=64, sa_type=String(64), nullable=False)
    last_name: str | None = Field(max_length=64, sa_type=String(64))
    photo_url: str | None


class UserBase(BriefUserBase):
    preferences: UserPreferences | None = Field(
        sa_type=JSONB, default_factory=UserPreferences, nullable=True
    )


class _UserIdModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class User(UserBase, _UserIdModel, table=True):
    __tablename__ = "user"

    collections: list["Collection"] = Relationship(back_populates="owner")
    cart: list["UserCartLink"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    pass


class UserPatch(SQLModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    photo_url: str | None = None

    preferences: UserPreferences | None = None


class _UserIdSchema(SQLModel):
    id: int


class BriefUserSchema(BriefUserBase, _UserIdSchema):
    pass


class UserSchema(UserBase, _UserIdSchema):
    collections: list["BriefCollectionSchema"] = []
    # cart: list["UserCartSchema"] = []  # maybe later


# AUTH


class AuthenticatedUser(SQLModel):
    id: int
    telegram_id: int


class AuthenticatedUserWithCollectionIds(AuthenticatedUser):
    collection_ids: set[UUID]


# CART


class UserCartBase(SQLModel):
    quantity: int = Field(ge=1, default=1, nullable=False)


class _UserCartIds(SQLModel):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", primary_key=True)
    product_id: UUID = Field(
        foreign_key="product.id", ondelete="CASCADE", primary_key=True
    )


class UserCartLink(UserCartBase, _UserCartIds, table=True):
    __tablename__ = "user_cart"

    user: User = Relationship(back_populates="cart")
    product: "Product" = Relationship()


class UserCartSchema(UserCartBase):
    product: "BriefProductSchema"
