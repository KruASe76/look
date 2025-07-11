from fastapi import APIRouter, HTTPException, status

from app.api.route.dependencies import DatabaseSession
from app.model import UserSchema
from app.service import UserService

from .. import messages
from ..util import build_responses

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get(
    "/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses({status.HTTP_404_NOT_FOUND: messages.USER_NOT_FOUND}),
    description="Get user by id",
)
async def get_user(user_id: int, session: DatabaseSession) -> ...:
    user_optional = await UserService.get_by_id(session, user_id)

    if not user_optional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )

    return user_optional
