from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel

from .catalog import Product


class UserCartBase(SQLModel):
    quantity: int = 1


class _UserCartIds(SQLModel):  # separate model for proper field order
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
    id: int = Field(primary_key=True)
    parameters: list[str] = Field(default_factory=list, sa_type=ARRAY(String))
    preferences: list[str] = Field(default_factory=list, sa_type=ARRAY(String))

    collections: list[str] = Field(default_factory=lambda: ["__FAVOURITE__"], sa_type=ARRAY(String))  # FIXME


class User(UserBase, table=True):
    __tablename__ = "user"

    cart: list[UserCartLink] = Relationship(back_populates="user")


class UserSchema(UserBase):
    cart: list[UserCartSchema] = []
