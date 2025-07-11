from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from . import BriefCollectionSchema, BriefProductSchema, Collection, Product


class BriefUserBase(SQLModel):
    telegram_id: int | None = Field(unique=True)
    username: str | None
    first_name: str
    last_name: str | None
    photo_url: str | None


class UserBase(BriefUserBase):
    preferences: dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)


class _UserIdModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class User(UserBase, _UserIdModel, table=True):
    __tablename__ = "user"

    collections: list["Collection"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    cart: list["UserCartLink"] = Relationship(
        back_populates="user", cascade_delete=True
    )


class UserCreate(UserBase):
    pass


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
    quantity: int = 1


class _UserCartIds(SQLModel):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    product_id: UUID = Field(foreign_key="product.id", primary_key=True)


class UserCartLink(UserCartBase, _UserCartIds, table=True):
    __tablename__ = "user_cart"

    user: User = Relationship(back_populates="cart")
    product: "Product" = Relationship()


class UserCartSchema(UserCartBase):
    product: "BriefProductSchema"
