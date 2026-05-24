from fastapi import APIRouter, Depends

from api.decorators import exception_handler
from db.uow import unit_of_work
from dependencies import get_current_user
from schemas.users import UserInfo
from services.access import AccessService
from services.user_profile import UserProfileService
from services.user_progress import UserProgressService

user_skill_router = APIRouter(prefix="/skills", tags=["SkillProgress"])



@user_skill_router.get("/available")
@exception_handler
async def get_available_skills_by_user(
    user_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_manage_user(user_id, current_user)
        return await UserProfileService(uow.session).get_available_skills(user_id)

@user_skill_router.get("/{skill_id}")
@exception_handler
async def get_user_skill_detail(
    user_id: int, skill_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        return await UserProfileService(uow.session).get_skill_progress(
            user_id, skill_id
        )


