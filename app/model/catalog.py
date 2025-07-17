from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, SQLModel


# noinspection PyTypeChecker
class BriefProductBase(SQLModel):
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
class ProductBase(BriefProductBase):
    description: str = Field(max_length=4096, sa_type=String(4096), nullable=False)


class Product(ProductBase, table=True):
    __tablename__ = "product"


class BriefProductSchema(BriefProductBase):
    pass


class ProductSchema(ProductBase):
    pass
