from fastapi import APIRouter, status

from app.api.route.dependencies import InitDataUser
from app.model import UserSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/init-data", response_model=UserSchema, status_code=status.HTTP_200_OK
)
async def auth_init_data(user: InitDataUser) -> ...:
    return user
