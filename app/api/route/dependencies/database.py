from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import spawn_readonly_session, spawn_session_with_transaction

DatabaseReadonlySession = Annotated[AsyncSession, Depends(spawn_readonly_session)]
DatabaseTransaction = Annotated[AsyncSession, Depends(spawn_session_with_transaction)]
