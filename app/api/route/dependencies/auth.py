from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase
from init_data_py import InitData
from init_data_py.errors.errors import InitDataPyError

from app.core.config import BOT_TOKEN
from app.model import User, UserCreate
from app.service import UserService

from .database import DatabaseTransaction


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


init_data_auth = HTTPBase(
    scheme=AuthConfig.init_data_scheme,
    description=AuthConfig.init_data_description,
    auto_error=False,
)

InitDataAuth = Annotated[HTTPAuthorizationCredentials | None, Depends(init_data_auth)]


async def process_init_data(auth: InitDataAuth, session: DatabaseTransaction) -> User:
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


InitDataUser = Annotated[User, Depends(process_init_data)]
