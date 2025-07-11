from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from . import BriefProductSchema, BriefUserSchema, Product, User


class CollectionProductLink(SQLModel, table=True):
    __tablename__ = "collection_product_link"

    collection_id: UUID = Field(foreign_key="collection.id", primary_key=True)
    product_id: UUID = Field(foreign_key="product.id", primary_key=True)


class CollectionBase(SQLModel):
    name: str
    cover_image_url: str | None = None


class _CollectionIdsModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
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
