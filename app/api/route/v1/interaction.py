from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, status

from app.core.exceptions import ProductNotFoundException
from app.model import InteractionType
from app.service import InteractionService

from ..auth import InitDataUser
from ..dependencies import DatabaseSession
from ..util import build_responses

interaction_router = APIRouter(prefix="/interaction", tags=["interaction"])


@interaction_router.put(
    "/product/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=build_responses(ProductNotFoundException, include_auth=True),
    summary="Record an interaction with a product for the user",
)
async def record_product_interaction(
    product_id: UUID,
    interaction_type: Annotated[InteractionType, Body(embed=True)],
    user: InitDataUser,
    session: DatabaseSession,
) -> None:
    await InteractionService.record_product_interaction(
        session, user.id, product_id, interaction_type
    )
