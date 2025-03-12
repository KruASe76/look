__all__ = ["DatabaseSession", "Pagination"]


from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import spawn_session

from .internal.pagination import PaginationSchema, pagination

Pagination = Annotated[PaginationSchema, Depends(pagination)]

DatabaseSession = Annotated[AsyncSession, Depends(spawn_session)]
