from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from app.core.exceptions import UserNotFoundException
from app.model import UserPatch, UserSchema
from app.service import UserService

from ..auth import InitDataUserFull
from ..dependencies import DatabaseSession
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
    responses=build_responses(UserNotFoundException),
    summary="Get user by id",
)
async def get_user(user_id: int, session: DatabaseSession) -> ...:
    return await UserService.get_by_id(session, user_id)
