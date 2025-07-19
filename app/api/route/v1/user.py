from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from app.model import UserPatch, UserSchema
from app.service import UserService

from .. import messages
from ..dependencies import DatabaseSession, InitDataUserFull
from ..util import build_responses

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.patch(
    "",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    summary="Partially update user",
)
async def patch_user(
    user_patch: Annotated[UserPatch, Body()],
    user: InitDataUserFull,
    session: DatabaseSession,
) -> ...:
    return await UserService.patch(session, user, user_patch)


@user_router.get(
    "/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses({status.HTTP_404_NOT_FOUND: messages.USER_NOT_FOUND}),
    summary="Get user by id",
)
async def get_user(user_id: int, session: DatabaseSession) -> ...:
    user_optional = await UserService.get_by_id(session, user_id)

    if user_optional is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )

    return user_optional
