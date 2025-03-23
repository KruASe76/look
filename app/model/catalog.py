from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel


class ReviewBase(SQLModel):
    author: str
    content: str
    rating: int = Field(ge=1, le=5)


class _ReviewId(SQLModel):  # separate model for proper field order
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    product_id: UUID = Field(foreign_key="product.id", ondelete="CASCADE")


class Review(ReviewBase, _ReviewId, table=True):
    __tablename__ = "product_review"


class ReviewSchema(ReviewBase):
    pass


# noinspection PyTypeChecker
class BriefProductBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    brand: str = Field(index=True)
    category: str = Field(index=True)
    sizes: list[str] = Field(default_factory=list, sa_type=ARRAY(String))
    colors: list[str] = Field(default_factory=list, sa_type=ARRAY(String))
    image_urls: list[str] = Field(sa_type=ARRAY(String))


class ProductBase(BriefProductBase):
    description: str


class Product(ProductBase, table=True):
    __tablename__ = "product"

    reviews: list[Review] = Relationship(cascade_delete=True)


class BriefProductSchema(BriefProductBase):
    pass


class ProductSchema(ProductBase):
    reviews: list[ReviewSchema] = []
