from pydantic import BaseModel


class SearchMeta(BaseModel):
    categories: list[str]
    colors: list[str]
    brands: list[str]
