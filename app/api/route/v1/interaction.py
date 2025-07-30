from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, status

from app.core.exceptions import ProductNotFoundException
from app.model import InteractionType
from app.service import CollectionService, InteractionService

from ..auth import InitDataUserWithCollectionIds
from ..dependencies import DatabaseTransaction
from ..util import build_responses

interaction_router = APIRouter(prefix="/interaction", tags=["interaction"])


@interaction_router.put(
    "/product/{product_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=build_responses(ProductNotFoundException, include_auth=True),
    summary="Record an interaction with a product for the user",
)
async def record_product_interaction(
    product_id: UUID,
    interaction_type: Annotated[InteractionType, Body(embed=True)],
    user: InitDataUserWithCollectionIds,
    session: DatabaseTransaction,
) -> None:
    await InteractionService.record_product_interaction(
        session=session,
        user_id=user.id,
        product_id=product_id,
        interaction_type=interaction_type,
    )

    # syncing user's default collection
    if interaction_type == InteractionType.LIKE:
        await CollectionService.add_products(
            session=session, user=user, collection_ids=[], product_ids=[product_id]
        )
    else:
        # if the product is included only to the default collection, remove it from there
        if (
            len(
                await CollectionService.check_product_inclusion(
                    session=session, user=user, product_id=product_id
                )
            )
            == 1
        ):
            await CollectionService.delete_products(
                session=session, user=user, collection_ids=[], product_ids=[product_id]
            )
