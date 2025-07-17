from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationSchema(BaseModel):
    limit: int = Field(gt=0, default=10)
    offset: int = Field(ge=0, default=0)


Pagination = Annotated[PaginationSchema, Query()]
