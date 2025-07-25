from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from init_data_py import InitData
from init_data_py.errors.errors import InitDataPyError

from app.core.config import BOT_TOKEN, INIT_DATA_SCHEME_NAME
from app.core.exceptions import (
    InitDataForbiddenException,
    InitDataUnauthorizedException,
)
from app.model import (
    AuthenticatedUser,
    AuthenticatedUserWithCollectionIds,
    User,
    UserCreate,
)
from app.service import UserService

from ..dependencies import DatabaseTransaction
from .config import AuthConfig


async def validate_init_data(
    auth: Annotated[
        HTTPAuthorizationCredentials | None, Depends(AuthConfig.init_data_scheme)
    ],
) -> InitData:
    if auth is None or auth.scheme != INIT_DATA_SCHEME_NAME:
        raise InitDataUnauthorizedException

    try:
        init_data = InitData.parse(auth.credentials)
    except InitDataPyError as e:
        raise InitDataForbiddenException from e

    if not (
        init_data.validate(bot_token=BOT_TOKEN, raise_error=False) and init_data.user
    ):
        raise InitDataForbiddenException

    return init_data


ValidInitData = Annotated[InitData, Depends(validate_init_data)]


async def get_full_user(init_data: ValidInitData, session: DatabaseTransaction) -> User:
    return await UserService.get_or_upsert(
        session,
        UserCreate(
            telegram_id=init_data.user.id,
            username=init_data.user.username,
            first_name=init_data.user.first_name,
            last_name=init_data.user.last_name,
            photo_url=init_data.user.photo_url,
        ),
    )


async def get_authenticated_user(
    init_data: ValidInitData, session: DatabaseTransaction
) -> AuthenticatedUser:
    user = await UserService.get_authenticated(session, init_data.user.id)

    if user is None:
        raise InitDataUnauthorizedException

    return user


async def get_authenticated_user_with_collection_ids(
    init_data: ValidInitData, session: DatabaseTransaction
) -> AuthenticatedUserWithCollectionIds:
    user = await UserService.get_authenticated_with_collection_ids(
        session, init_data.user.id
    )

    if user is None:
        raise InitDataUnauthorizedException

    return user


InitDataUserFull = Annotated[User, Depends(get_full_user)]
InitDataUser = Annotated[AuthenticatedUser, Depends(get_authenticated_user)]
InitDataUserWithCollectionIds = Annotated[
    AuthenticatedUserWithCollectionIds,
    Depends(get_authenticated_user_with_collection_ids),
]
