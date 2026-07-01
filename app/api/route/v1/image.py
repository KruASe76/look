import hashlib
from typing import Annotated

from anyio import Path
from fastapi import APIRouter, Query, status
from fastapi.responses import FileResponse

from app.core.config import IMAGE_CONTENT_TYPE, IMAGE_DIR, IMAGE_EXTENSION, IMAGE_HEADERS
from app.core.exceptions import NotFoundError

from ..util import build_responses

image_router = APIRouter(prefix="/image", tags=["image"])


@image_router.get(
    "",
    response_model=None,
    status_code=status.HTTP_200_OK,
    responses=build_responses(NotFoundError),
    summary="Get image by URL",
)
async def get_image(url: Annotated[str, Query()]) -> ...:
    file_path = Path(IMAGE_DIR / f"{hashlib.sha256(url.encode()).hexdigest()}.{IMAGE_EXTENSION}")

    if not await file_path.exists():
        raise NotFoundError

    return FileResponse(path=file_path, media_type=IMAGE_CONTENT_TYPE, headers=IMAGE_HEADERS)
