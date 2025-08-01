from datetime import datetime
from uuid import UUID

from pydantic import PrivateAttr
from sqlalchemy import Column, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship as sa_relationship
from sqlmodel import Field, Relationship, SQLModel


# noinspection PyTypeChecker
class ProductColorGroup(SQLModel, table=True):
    __tablename__ = "product_color_group"

    product_id: UUID = Field(
        foreign_key="product.id",
        ondelete="CASCADE",
        primary_key=True,
        sa_type=PG_UUID(as_uuid=True),
    )
    color_group_id: UUID = Field(
        nullable=False, index=True, sa_type=PG_UUID(as_uuid=True)
    )

    color_code: str = Field(
        min_length=7, max_length=7, sa_type=String(7), nullable=False
    )
    color_name: str = Field(max_length=50, sa_type=String(50), nullable=False)


class ProductColorGroupSchema(SQLModel):
    product_id: UUID
    color_code: str
    color_name: str


# noinspection PyTypeChecker
class _BriefProductBase(SQLModel):
    id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    article: str = Field(unique=True, max_length=50, sa_type=String(50), nullable=False)

    name: str = Field(max_length=255, sa_type=String(255), nullable=False)
    brand: str = Field(max_length=255, sa_type=String(255), nullable=False)
    category: str = Field(max_length=50, sa_type=String(50), nullable=False)

    color_code: str = Field(
        min_length=7, max_length=7, sa_type=String(7), nullable=False
    )
    color_name: str = Field(max_length=50, sa_type=String(50), nullable=False)
    color_group_id: UUID = Field(nullable=False, sa_type=PG_UUID(as_uuid=True))

    sizes: list[str] = Field(
        sa_column=Column(ARRAY(String), server_default="{}", nullable=False),
        default_factory=list,
    )
    image_urls: list[str] = Field(
        sa_column=Column(ARRAY(String), server_default="{}", nullable=False),
        default_factory=list,
    )

    price: float = Field(ge=0, nullable=False)
    discount_price: float = Field(ge=0, nullable=False)

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            server_onupdate=func.now(),
            nullable=False,
        )
    )


# noinspection PyTypeChecker
class _ProductBase(_BriefProductBase):
    original_url: str = Field(nullable=False)
    description: str = Field(max_length=4096, sa_type=String(4096), nullable=False)
    details: dict[str, str] = Field(sa_type=JSONB, nullable=False)


class Product(_ProductBase, table=True):
    __tablename__ = "product"

    color_group: list[ProductColorGroup] = Relationship(
        sa_relationship=sa_relationship(
            "ProductColorGroup",
            primaryjoin="Product.color_group_id == foreign(ProductColorGroup.color_group_id)",
            order_by="ProductColorGroup.color_name",
            viewonly=True,
        )
    )

    # non-db fields
    _is_contained_in_user_collections: bool = PrivateAttr()

    @property
    def is_contained_in_user_collections(self) -> bool:
        return self._is_contained_in_user_collections

    @is_contained_in_user_collections.setter
    def is_contained_in_user_collections(self, value: bool) -> None:
        self._is_contained_in_user_collections = value


class _ProductSchemaExtra(SQLModel):
    color_group_id: UUID = Field(exclude=True)

    is_contained_in_user_collections: bool


class BriefProductSchema(_ProductSchemaExtra, _BriefProductBase):
    pass


class ProductSchema(_ProductSchemaExtra, _ProductBase):
    color_group: list[ProductColorGroupSchema] = []
