from pydantic import BaseModel, Field


class SearchMeta(BaseModel):
    brands: list[str]
    categories: list[str]
    colors: dict[str, str] = Field(description="Mapping of color names to their hex codes")
