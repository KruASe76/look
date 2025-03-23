from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase
from init_data_py import InitData
from init_data_py.errors.errors import InitDataPyError
from pydantic import BaseModel

from app.core.config import BOT_TOKEN
from app.model import User
from app.service import TokenService, UserService

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

    init_data_lifetime = 300  # 5 minutes

    jwt_schema_title = "JWT pair"
    jwt_schema_description = (
        "At least one of the tokens should be valid for request to succeed"
    )

    jwt_unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT cookies missing"
    )
    jwt_forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="JWT pair invalid or refresh-token expired",
    )


init_data_auth = HTTPBase(
    scheme=AuthConfig.init_data_scheme,
    description=AuthConfig.init_data_description,
    auto_error=False,
)

InitDataAuth = Annotated[HTTPAuthorizationCredentials | None, Depends(init_data_auth)]


class TokenPair(BaseModel):
    access_token: str | None
    refresh_token: str | None


TokenPairCookie = Annotated[
    TokenPair,
    Cookie(
        title=AuthConfig.jwt_schema_title, description=AuthConfig.jwt_schema_description
    ),
]


def _generate_tokens_and_populate_response(user_id: int, response: Response) -> None:
    access_token, refresh_token = TokenService.generate_token_pair(user_id)

    response.set_cookie(
        "access_token", access_token, httponly=True, secure=True, samesite="strict"
    )
    response.set_cookie(
        "refresh_token", refresh_token, httponly=True, secure=True, samesite="strict"
    )


async def process_init_data(
    auth: InitDataAuth,
    response: Response,
    session: DatabaseTransaction
) -> User:
    if auth is None or auth.scheme != AuthConfig.init_data_scheme:
        raise AuthConfig.init_data_unauthorized_exception

    try:
        init_data = InitData.parse(auth.credentials)
    except InitDataPyError as e:
        raise AuthConfig.init_data_forbidden_exception from e

    if not (
        init_data.validate(bot_token=BOT_TOKEN, lifetime=AuthConfig.init_data_lifetime, raise_error=False)
        and init_data.user
    ):
        raise AuthConfig.init_data_forbidden_exception

    user = await UserService.create_user(
        telegram_id=init_data.user.id,
        username=init_data.user.username,
        first_name=init_data.user.first_name,
        last_name=init_data.user.last_name,
        session=session,
    )

    _generate_tokens_and_populate_response(user.id, response)

    return user


async def process_jwt(token_pair: TokenPairCookie, response: Response) -> int:
    if not (token_pair.access_token or token_pair.refresh_token):
        raise AuthConfig.init_data_unauthorized_exception

    try:
        return TokenService.decode_token(token_pair.access_token)
    except ValueError:
        try:
            user_id = TokenService.decode_token(token_pair.refresh_token)
        except ValueError as e:
            raise AuthConfig.jwt_forbidden_exception from e

        _generate_tokens_and_populate_response(user_id, response)

        return user_id


InitDataUser = Annotated[User, Depends(process_init_data)]
JWTUserId = Annotated[int, Depends(process_jwt)]
