from uuid import UUID, uuid4

from pydantic import HttpUrl
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel


class ReviewBase(SQLModel):
    author: str
    content: str
    rating: int = Field(ge=1, le=5)


class _ReviewId(SQLModel):  # separate model to order fields properly
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    product_id: UUID = Field(foreign_key="products.id", ondelete="CASCADE")


class Review(ReviewBase, _ReviewId, table=True):
    __tablename__ = "reviews"


class ReviewSchema(ReviewBase):
    pass


# noinspection PyTypeChecker
class BriefProductBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    brand: str = Field(index=True)
    sizes: list[str] = Field(default_factory=list, sa_type=ARRAY(String))
    colors: list[str] = Field(default_factory=list, sa_type=ARRAY(String))
    image_urls: list[HttpUrl] = Field(sa_type=ARRAY(String))


class ProductBase(BriefProductBase):
    description: str


class Product(ProductBase, table=True):
    __tablename__ = "products"

    reviews: list[Review] = Relationship(cascade_delete=True)


class BriefProductSchema(BriefProductBase):
    pass


class ProductSchema(ProductBase):
    reviews: list[ReviewSchema] = []
