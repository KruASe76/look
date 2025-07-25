from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import field_validator
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from .misc import UserPreferences

if TYPE_CHECKING:
    from . import BriefCollectionSchema, BriefProductSchema, Collection, Product


# noinspection PyTypeChecker
class _UserBase(SQLModel):
    telegram_id: int | None = Field(unique=True)
    username: str | None = Field(max_length=64, sa_type=String(64))
    first_name: str = Field(max_length=64, sa_type=String(64), nullable=False)
    last_name: str | None = Field(max_length=64, sa_type=String(64))
    photo_url: str | None


class _UserPreferencesSchema(SQLModel):
    preferences: UserPreferences | None = Field(default_factory=UserPreferences)


class _UserIdModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class User(_UserBase, _UserIdModel, table=True):
    __tablename__ = "user"

    preferences_data: dict | None = Field(
        sa_column=Column(JSONB, name="preferences", server_default=None, nullable=True),
        default_factory=lambda: UserPreferences().model_dump(),
    )

    collections: list["Collection"] = Relationship(back_populates="owner")
    cart: list["UserCartLink"] = Relationship(back_populates="user")

    @property
    def preferences(self) -> UserPreferences:
        return UserPreferences(**self.preferences_data or {})

    @preferences.setter
    def preferences(self, value: UserPreferences) -> None:
        if value is not None:
            self.preferences_data = value.model_dump()


class UserCreate(_UserPreferencesSchema, _UserBase):
    pass


class UserPatch(SQLModel):
    telegram_id: int | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    photo_url: str | None = None

    preferences: UserPreferences | None = None


class _UserIdSchema(SQLModel):
    id: int


class BriefUserSchema(_UserBase, _UserIdSchema):
    pass


class UserWithPreferencesSchema(_UserPreferencesSchema, BriefUserSchema):
    pass


class UserSchema(UserWithPreferencesSchema):
    collections: list["BriefCollectionSchema"] = []
    # cart: list["UserCartSchema"] = []  # maybe later

    @staticmethod
    @field_validator("collections", mode="before")
    def sort_collections(value: ...) -> list["Collection"]:
        if value and isinstance(value, list):
            return sorted(
                value,
                key=lambda c: c.created_at,
            )
        return value


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
