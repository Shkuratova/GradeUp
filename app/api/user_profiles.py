from fastapi import APIRouter, Depends

from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from dependencies import get_current_user
from schemas.user_profile import UserProfileAdd, UserProfileProgressList
from schemas.users import UserInfo
from services import EventService
from services.access import AccessService
from services.user_profile import UserProfileService
from utils.roles import UserRole

user_profile_router = APIRouter(prefix="/users/profiles", tags=["Users", "UserProfiles"])


@user_profile_router.get("/", response_model=list[UserProfileProgressList])
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await UserProfileService(uow.session).get_all_with_progress()


@user_profile_router.post("/")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def add(
    user_profile: UserProfileAdd, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_manage_user(
            user_profile.user_id, current_user
        )
        new_user_profile = await UserProfileService(uow.session).create(user_profile)
        await EventService(uow.session).log_set_user_profile(new_user_profile, current_user)
        return new_user_profile


user_profile_detail_router = APIRouter(prefix="/profiles/{profile_id}", tags=["ProfileProgress"])


@user_profile_detail_router.get("")
@exception_handler
async def get_by_id(
    user_id: int, profile_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_user_profile(
            user_id, profile_id, current_user
        )
        return await UserProfileService(uow.session).status(user_id, profile_id)


@user_profile_detail_router.post("/grade-up")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def gradeup_user(
    user_id: int, profile_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_user_profile(
            user_id, profile_id, current_user
        )
        await UserProfileService(uow.session).gradeup(user_id, profile_id)
        await EventService(uow.session).log_gradeup(user_id, profile_id, current_user)

