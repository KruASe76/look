from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from . import BriefProductSchema, BriefUserSchema, Product, User


# noinspection PyTypeChecker
class CollectionProductLink(SQLModel, table=True):
    __tablename__ = "collection_product_link"

    collection_id: UUID = Field(
        foreign_key="collection.id",
        ondelete="CASCADE",
        primary_key=True,
        sa_type=PG_UUID(as_uuid=True),
    )
    product_id: UUID = Field(
        foreign_key="product.id",
        ondelete="CASCADE",
        primary_key=True,
        sa_type=PG_UUID(as_uuid=True),
    )


# noinspection PyTypeChecker
class _CollectionBase(SQLModel):
    name: str = Field(max_length=255, sa_type=String(255), nullable=False)
    cover_image_url: str | None = None


class _CollectionIdsModel(SQLModel):
    id: UUID | None = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        ),
        default=None,
    )
    owner_id: int = Field(foreign_key="user.id", ondelete="CASCADE", index=True)


class Collection(_CollectionBase, _CollectionIdsModel, table=True):
    __tablename__ = "collection"

    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
        default=None,
    )

    owner: "User" = Relationship(back_populates="collections")
    products: list["Product"] = Relationship(link_model=CollectionProductLink)


class CollectionCreate(_CollectionBase):
    pass


class CollectionPatch(SQLModel):
    name: str | None = None
    cover_image_url: str | None = None


class _CollectionIdSchema(SQLModel):
    id: UUID


class BriefCollectionSchema(_CollectionBase, _CollectionIdSchema):
    pass


class CollectionSchema(BriefCollectionSchema):
    products: list["BriefProductSchema"] = []


class CollectionSchemaWithOwner(CollectionSchema):
    owner: "BriefUserSchema"
