from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel


# noinspection PyTypeChecker
class BriefProductBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    brand: str = Field(index=True)
    category: str = Field(index=True)
    sizes: list[str] = Field(default_factory=list, sa_type=ARRAY(String))
    color: str = Field(index=True)
    image_urls: list[str] = Field(sa_type=ARRAY(String))
    # to be modified...


class ProductBase(BriefProductBase):
    description: str


class Product(ProductBase, table=True):
    __tablename__ = "product"


class BriefProductSchema(BriefProductBase):
    pass


class ProductSchema(ProductBase):
    pass
