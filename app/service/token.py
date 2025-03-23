from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.core.config import PRIVATE_KEY, PUBLIC_KEY


class TokenService:
    _jwt_algorithm = "RS256"

    @classmethod
    def generate_token_pair(cls, user_id: int) -> tuple[str, str]:
        """Generate ``access_token`` and ``refresh_token`` with the subject of ``user_id``"""
        now = datetime.now(UTC)

        payload = {"sub": str(user_id)}

        access_token = jwt.encode(
            payload=payload | {"exp": now + timedelta(minutes=5)},
            key=PRIVATE_KEY,
            algorithm=cls._jwt_algorithm,
        )
        refresh_token = jwt.encode(
            payload=payload | {"exp": now + timedelta(days=7)},
            key=PRIVATE_KEY,
            algorithm=cls._jwt_algorithm,
        )

        return access_token, refresh_token

    @classmethod
    def decode_token(cls, token: str) -> int:
        """Decode ``token`` and return ``user_id``"""
        try:
            payload = jwt.decode(
                jwt=token, key=PUBLIC_KEY, algorithms=(cls._jwt_algorithm,)
            )

            return int(payload["sub"])
        except InvalidTokenError as e:
            raise ValueError from e
