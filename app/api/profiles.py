from fastapi import APIRouter, Depends, HTTPException, status
from services.profile import ProfileService, LevelService
from services.skill import LevelSkillService
from db.uow import unit_of_work
from schemas.profiles import (
    ProfileAdd,
    SProfile,
    LevelAdd,
    ProfileLevels,
    LevelSkillAdd,
    LevelSkill,
    SProfileAdd,
)
from api.decorators import check_role, exception_handler
from dependencies.auth import get_current_user
from api.roles import UserRole
from schemas.users import UserInfo

profile_router = APIRouter(prefix="/profile", tags=["Profiles"])


@profile_router.get("", response_model=list[SProfile])
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        service = ProfileService(uow.session)
        if current_user.role_name == UserRole.SUPERVISOR:
            if current_user.department_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Руководитель не привязан к отделу.",
                )
            return await service.get_all_by_department_id(current_user.department_id)
        return await service.get_all()


@profile_router.post("")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(profile: SProfileAdd, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).add_profile(profile)


@profile_router.get("/{profile_id}")
@exception_handler
async def get_by_id(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).get_with_details(profile_id)


@profile_router.post("/{profile_id}/levels")
@exception_handler
async def add_level(
    profile_id: int, level: LevelAdd, current_user=Depends(get_current_user)
):
    level.profile_id = profile_id
    with unit_of_work() as uow:
        return await LevelService(uow.session).add(level)


@profile_router.get("/{profile_id}/levels", response_model=ProfileLevels)
@exception_handler
async def get_levels(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).get_profile_levels(profile_id)


@profile_router.get("/{profile_id}/levels", response_model=ProfileLevels)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_levels(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).get_profile_levels(profile_id)


@profile_router.post("/levels")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add_skill(
    level_skill: LevelSkillAdd,
    current_user=Depends(get_current_user),
):
    async with unit_of_work() as uow:
        await LevelSkillService(uow.session).add(level_skill)
        return {"detail": "Навык добавлен к уровню."}
