from typing import Annotated

from fastapi import APIRouter, Body, status

from app.core.exceptions import UserNotFoundException
from app.model import UserPatch, UserSchema, UserWithPreferencesSchema
from app.service import UserService

from ..auth import InitDataUser, InitDataUserFull
from ..dependencies import DatabaseTransaction
from ..util import build_responses

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get(
    "/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses(UserNotFoundException),
    summary="Get user by id",
)
async def get_user(user_id: int, session: DatabaseTransaction) -> ...:
    return await UserService.get_by_id(session=session, user_id=user_id)


@user_router.patch(
    "",
    response_model=UserWithPreferencesSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    summary="Partially update user",
)
async def patch_user(
    user_patch: Annotated[UserPatch, Body()],
    user: InitDataUserFull,
    session: DatabaseTransaction,
) -> ...:
    return await UserService.patch(session=session, user=user, user_patch=user_patch)


@user_router.delete(
    "",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=build_responses(include_auth=True),
    summary="Delete user",
)
async def delete_user(user: InitDataUser, session: DatabaseTransaction) -> ...:
    await UserService.delete_by_id(session=session, user_id=user.id)
