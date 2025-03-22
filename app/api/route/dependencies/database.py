from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import spawn_session, spawn_session_with_transaction

DatabaseSession = Annotated[AsyncSession, Depends(spawn_session)]
DatabaseTransaction = Annotated[AsyncSession, Depends(spawn_session_with_transaction)]
