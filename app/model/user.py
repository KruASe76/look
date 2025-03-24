from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel

from .catalog import Product


class UserCartBase(SQLModel):
    quantity: int = 1


class _UserCartIds(SQLModel):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    product_id: UUID = Field(foreign_key="product.id", primary_key=True)


class UserCartLink(UserCartBase, _UserCartIds, table=True):
    __tablename__ = "user_cart"

    user: "User" = Relationship(back_populates="cart")
    product: Product = Relationship()


class UserCartSchema(UserCartBase):
    product: Product


# noinspection PyTypeChecker
class UserBase(SQLModel):
    telegram_id: int | None = Field(unique=True)
    username: str | None
    first_name: str
    last_name: str | None
    photo_url: str | None

    parameters: list[str] = Field(default_factory=list, sa_type=ARRAY(String))
    preferences: list[str] = Field(default_factory=list, sa_type=ARRAY(String))

    collections: list[str] = Field(
        default_factory=lambda: ["__FAVOURITE__"], sa_type=ARRAY(String)
    )  # FIXME


class UserCreate(UserBase):
    pass


class _UserIdModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class User(UserBase, _UserIdModel, table=True):
    __tablename__ = "user"

    cart: list[UserCartLink] = Relationship(back_populates="user", cascade_delete=True)


class _UserIdSchema(SQLModel):
    id: int


class UserSchema(UserBase, _UserIdSchema):
    cart: list[UserCartSchema] = []
