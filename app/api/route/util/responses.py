__all__ = ["PydanticResponse"]

from collections.abc import Mapping

from fastapi import Response
from pydantic import BaseModel
from starlette.background import BackgroundTask


class PydanticResponse(Response):
    media_type = "application/json"

    def __init__(
        self,
        content: BaseModel,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: BaseModel) -> bytes:
        return content.model_dump_json().encode(self.charset)
