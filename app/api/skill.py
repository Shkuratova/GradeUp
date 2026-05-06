from fastapi import APIRouter, Depends, Query
from typing import Annotated

from fastapi.params import Depends
from dependencies.auth import get_current_user
from api.roles import UserRole
from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from services.skill import SkillService, StageService
from schemas.users import UserInfo
from schemas.skills import (
    SkillAdd,
    SkillSchema,
    SkillFilter,
    StageAdd,
    SkillBase,
    SkillDetail,
    SkillStages,
    SkillAddForm,
    SkillUpdateForm,
)

skill_router = APIRouter(prefix="/skills", tags=["Skill"])


@skill_router.get("/", response_model=list[SkillSchema])
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(
    skill_filter: Annotated[SkillFilter, Query()],
    current_user=Depends(get_current_user),
):
    async with unit_of_work() as uow:
        return await SkillService(uow.session).get_all_by_categories(skill_filter)


@skill_router.get("/stages", response_model=list[SkillStages])
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all_with_stages(
    skill_filter: Annotated[SkillFilter, Query()],
    current_user=Depends(get_current_user),
):
    async with unit_of_work() as uow:
        return await SkillService(uow.session).get_skills_stages(skill_filter)


@skill_router.post("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(skill: SkillAddForm, current_user: UserInfo = Depends(get_current_user)):
    skill.skill.creator_id = current_user.id
    async with unit_of_work() as uow:
        new_skill = await SkillService(uow.session).add_skill(skill)
        return new_skill


@skill_router.get("/{skill_id}", response_model=SkillDetail)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_by_id(skill_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        skill = await SkillService(uow.session).get_skill_with_questions(skill_id)
        return skill


@skill_router.put("/{skill_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update(
    skill_id: int, skill: SkillUpdateForm, current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        new_skill = await SkillService(uow.session).update_by_id(skill_id, skill)
        return new_skill


@skill_router.patch("/{skill_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def partial_update(
    skill_id: int, skill: SkillUpdateForm, current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await SkillService(uow.session).partial_update(skill_id, skill)


@skill_router.post("/{skill_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add_stage(
    skill_id: int, stage: StageAdd, current_user=Depends(get_current_user)
):
    stage.skill_id = skill_id
    async with unit_of_work() as uow:
        new_stage = await StageService(uow.session).add(stage)
        return new_stage


@skill_router.delete("/{skill_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def delete_skill(skill_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await SkillService(uow.session).soft_delete_by_id(skill_id)
        return {"detail": f"Навык с id = {skill_id} был удален."}
