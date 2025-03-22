from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, Field


class PaginationSchema(BaseModel):
    limit: int = Field(gt=0)
    offset: int = Field(ge=0)


def pagination(
    limit: Annotated[int, Query(gt=0)] = 10, offset: Annotated[int, Query(ge=0)] = 0
) -> PaginationSchema:
    return PaginationSchema(limit=limit, offset=offset)


Pagination = Annotated[PaginationSchema, Depends(pagination)]
