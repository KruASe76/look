import re
from functools import cache

from fastapi import status
from frozendict import frozendict
from pydantic import create_model

from .dependencies.auth import AuthConfig

WORD_MATCHING_REGEX = re.compile("[a-z]+", re.IGNORECASE)


@cache
def _string_to_class_name(string: str) -> str:
    return "_" + "".join([s.capitalize() for s in WORD_MATCHING_REGEX.findall(string)])


@cache
def _build_responses_internal(
    status_code_to_message: frozendict[int, str],
) -> dict[int, dict[str, ...]]:
    return {
        status_code: {
            "model": create_model(_string_to_class_name(message), detail=(str, message))
        }
        for status_code, message in status_code_to_message.items()
    }


def build_responses(
    status_code_to_message: dict[int, str] | None = None,
    /,
    *,
    include_auth: bool = False,
    include_dev_auth: bool = False,
) -> dict[int, dict[str, ...]]:
    defaults = {}

    if include_auth:
        defaults |= {
            status.HTTP_401_UNAUTHORIZED: AuthConfig.init_data_unauthorized_exception.detail,
            status.HTTP_403_FORBIDDEN: AuthConfig.init_data_forbidden_exception.detail,
        }

    if include_dev_auth:
        defaults |= {
            status.HTTP_403_FORBIDDEN: AuthConfig.api_key_forbidden_exception.detail
        }

    return _build_responses_internal(
        frozendict(defaults | (status_code_to_message or {}))
    )
