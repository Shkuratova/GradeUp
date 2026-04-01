from fastapi import APIRouter, Depends, Query
from typing import Annotated
from api.decorators import check_role
from dependencies.auth import get_current_user
from api.roles import UserRole
from schemas.users import UserInfo
from services.skill import skill_service as service
from schemas.skills import SkillAdd, SkillInfo, SkillUpdate, SkillFilter
from api.decorators import exception_handler

skill_router = APIRouter(prefix="/skills", tags=["Skill"])

@skill_router.get("/", response_model=list[SkillInfo])
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(
        skill_filter: Annotated[SkillFilter, Query()],
        current_user = Depends(get_current_user)):
    return  await service.get_all(filter_model=skill_filter)

@skill_router.post("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(skill: SkillAdd, current_user: UserInfo = Depends(get_current_user)):
    skill.creator_id = current_user.id
    new_skill = await service.add(skill)
    return new_skill



@skill_router.get("/{skill_id}", response_model=SkillInfo)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_by_id(skill_id: int, current_user = Depends(get_current_user)):
    skill = await service.get_by_id(skill_id)
    return skill


@skill_router.patch("/{skill_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update(skill_id: int, skill: SkillUpdate, current_user= Depends(get_current_user)):
    await service.update_by_id(skill_id, skill)
    return {"detail": "Навык успешно обновлен."}


@skill_router.post("/{skill_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add_stage():
    pass

