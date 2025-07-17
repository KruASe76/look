from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase
from init_data_py import InitData
from init_data_py.errors.errors import InitDataPyError

from app.core.config import BOT_TOKEN, DEV_API_KEY
from app.model import (
    AuthenticatedUser,
    AuthenticatedUserWithCollectionIds,
    User,
    UserCreate,
)
from app.service import UserService

from .database import DatabaseSession, DatabaseTransaction


class AuthConfig:
    init_data_scheme = "tma"

    init_data_description = "Telegram MiniApp init-data"

    init_data_unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"{init_data_scheme.upper()} init-data missing",
        headers={
            "WWW-Authenticate": (
                f'{init_data_scheme.upper()} realm="initial authentication", '
                f'error="missing"'
            )
        },
    )
    init_data_forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"{init_data_scheme.upper()} init-data invalid or expired",
    )

    api_key_scheme = APIKeyHeader(name="x-api-key")

    api_key_forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="API key is missing or invalid"
    )


init_data_auth = HTTPBase(
    scheme=AuthConfig.init_data_scheme,
    description=AuthConfig.init_data_description,
    auto_error=False,
)

InitDataAuth = Annotated[HTTPAuthorizationCredentials | None, Depends(init_data_auth)]


async def validate_init_data(auth: InitDataAuth) -> InitData:
    if auth is None or auth.scheme != AuthConfig.init_data_scheme:
        raise AuthConfig.init_data_unauthorized_exception

    try:
        init_data = InitData.parse(auth.credentials)
    except InitDataPyError as e:
        raise AuthConfig.init_data_forbidden_exception from e

    if not (
        init_data.validate(bot_token=BOT_TOKEN, raise_error=False) and init_data.user
    ):
        raise AuthConfig.init_data_forbidden_exception

    return init_data


ValidInitData = Annotated[InitData, Depends(validate_init_data)]


async def get_full_user(init_data: ValidInitData, session: DatabaseTransaction) -> User:
    return await UserService.get_or_create(
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
    init_data: ValidInitData, session: DatabaseSession
) -> AuthenticatedUser:
    user = await UserService.get_authenticated(session, init_data.user.id)

    if user is None:
        raise AuthConfig.init_data_unauthorized_exception

    return user


async def get_authenticated_user_with_collection_ids(
    init_data: ValidInitData, session: DatabaseSession
) -> AuthenticatedUserWithCollectionIds:
    user = await UserService.get_authenticated_with_collection_ids(
        session, init_data.user.id
    )

    if user is None:
        raise AuthConfig.init_data_unauthorized_exception

    return user


InitDataUserFull = Annotated[User, Depends(get_full_user)]
InitDataUser = Annotated[AuthenticatedUser, Depends(get_authenticated_user)]
InitDataUserWithCollectionIds = Annotated[
    AuthenticatedUserWithCollectionIds,
    Depends(get_authenticated_user_with_collection_ids),
]


async def validate_api_key(api_key: str = Depends(AuthConfig.api_key_scheme)) -> None:
    if not DEV_API_KEY or api_key != DEV_API_KEY:
        raise AuthConfig.api_key_forbidden_exception


DevAPIKey = Depends(validate_api_key)
