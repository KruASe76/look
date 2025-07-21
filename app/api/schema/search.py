from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query: str | None = None
    categories: list[str] | None = None
    colors: list[str] | None = None
    brands: list[str] | None = None
    min_price: float | None = Field(None, ge=0)
    max_price: float | None = Field(None, ge=0)


class SearchSuggestionQuery(BaseModel):
    query: str | None = None
    limit: int = Field(10, ge=1, le=100)
