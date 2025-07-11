from fastapi import APIRouter, status

from app.api.route.dependencies import InitDataUserFull
from app.model import UserSchema

from ..util import build_responses

auth_router = APIRouter(prefix="/auth", tags=["user"])


@auth_router.post(
    "/init-data",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    responses=build_responses(include_auth=True),
    description="Authenticate user and return user data",
)
async def auth_init_data(user: InitDataUserFull) -> ...:
    return user
