from pydantic import BaseModel


class ProductDetails(BaseModel):
    article: str
    brand: str
    country: str
    composition: str


class SearchMeta(BaseModel):
    categories: list[str]
    colors: list[str]
    brands: list[str]
