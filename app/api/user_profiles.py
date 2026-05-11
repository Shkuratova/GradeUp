from fastapi import APIRouter, Depends

from db.uow import unit_of_work
from dependencies import get_current_user
from api.decorators import exception_handler, check_role
from schemas.user_profile import UserProfileAdd, UserProfileProgressList
from services.user_profile import UserProfileService
from utils.roles import UserRole
from schemas.users import UserInfo

user_profile_router = APIRouter(prefix="/user-profiles", tags=["UserProfiles"])


@user_profile_router.get("/", response_model=list[UserProfileProgressList])
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await UserProfileService(uow.session).get_all_with_progress()

@user_profile_router.post("/")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def add(user_profile: UserProfileAdd, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await UserProfileService(uow.session).create(user_profile)


@user_profile_router.get("/{user_profile_id}")
@exception_handler
async def get_by_id(
    user_profile_id: int, current_user: UserInfo = Depends(get_current_user)
):
    pass
