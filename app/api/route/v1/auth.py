from fastapi import APIRouter, status

from app.api.route.dependencies import DatabaseTransaction, InitDataUserId
from app.model.user import UserSchema
from app.service.user import UserService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/init-data", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def auth_init_data(user_id: InitDataUserId, session: DatabaseTransaction) -> ...:
    return await UserService.create_user(user_id, session)
