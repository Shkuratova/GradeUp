from typing import Annotated
from fastapi import APIRouter, Depends, Query

from db.uow import unit_of_work
from dependencies import get_current_user
from api.decorators import exception_handler, check_role
from schemas.user_profile import UserProfileAdd, UserProfileProgressList, UserStageAdd
from services.user_profile import UserProfileService
from services.user_stage import UserStageService
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


@user_profile_router.get("/level-skills")
@exception_handler
async def get_available_skills_by_user(user_id: int, current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await UserProfileService(uow.session).get_available_skills(user_id)

@user_profile_router.get("/skills")
@exception_handler
async def get_user_skill_detail(user_id: Annotated[int, Query()], skill_id: Annotated[int, Query()], current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await UserProfileService(uow.session).get_skill_progress(user_id, skill_id)

@user_profile_router.post("/stages")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def evaluate(user_stage: UserStageAdd, current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        await UserStageService(uow.session).evaluate(user_stage)


@user_profile_router.get("/stages/{user_stage_id}")
@exception_handler
async def get(user_stage_id: int, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        pass

@user_profile_router.get("/{user_profile_id}")
@exception_handler
async def get_by_id(
    user_profile_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        return await UserProfileService(uow.session).status(user_profile_id)

@user_profile_router.post("/{user_profile_id}")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def gradeup_user(user_profile_id: int, current_user : UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        # logs
        await UserProfileService(uow.session).gradeup(user_profile_id)


