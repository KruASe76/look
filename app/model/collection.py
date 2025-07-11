from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from . import BriefProductSchema, BriefUserSchema, Product, User


class CollectionProductLink(SQLModel, table=True):
    __tablename__ = "collection_product_link"

    collection_id: UUID = Field(foreign_key="collection.id", primary_key=True)
    product_id: UUID = Field(foreign_key="product.id", primary_key=True)


# noinspection PyTypeChecker
class CollectionBase(SQLModel):
    name: str = Field(max_length=255, sa_type=String(255), nullable=False)
    cover_image_url: str | None = None


class _CollectionIdsModel(SQLModel):
    id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    owner_id: int = Field(foreign_key="user.id", index=True)


class Collection(CollectionBase, _CollectionIdsModel, table=True):
    __tablename__ = "collection"

    owner: "User" = Relationship(back_populates="collections")
    products: list["Product"] = Relationship(link_model=CollectionProductLink)


class CollectionCreate(CollectionBase):
    pass


class _CollectionIdSchema(SQLModel):
    id: UUID


class BriefCollectionSchema(CollectionBase, _CollectionIdSchema):
    pass


class CollectionSchema(BriefCollectionSchema):
    owner: "BriefUserSchema"
    products: list["BriefProductSchema"] = []
