from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.params import Depends

from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from dependencies.auth import get_current_user
from schemas.profiles import SkillList
from schemas.skills import (
    SkillSchema,
    SkillFilter,
    SkillDetail,
    SkillAddForm,
    SkillUpdateForm,
)
from schemas.users import UserInfo
from services import AccessService, SkillService
from utils.roles import UserRole

skill_router = APIRouter(prefix="/skills", tags=["Skill"])


@skill_router.get(
    "/", response_model=list[SkillList], summary="Получить список навыков"
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(
    skill_filter: Annotated[SkillFilter, Query()],
    current_user=Depends(get_current_user),
):
    async with unit_of_work() as uow:
        return await SkillService(uow.session).get_list(skill_filter)


@skill_router.post(
    "/",
    response_model=SkillDetail,
    summary="Добавить навык с этапами и вопросами этапов",
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(skill: SkillAddForm, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        new_skill = await SkillService(uow.session).add_skill(skill)
        return new_skill


@skill_router.get(
    "/stages",
    response_model=list[SkillSchema],
    summary="Получить список навыков с этапами",
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(
    skill_filter: Annotated[SkillFilter, Query()],
    current_user=Depends(get_current_user),
):
    async with unit_of_work() as uow:
        return await SkillService(uow.session).get_all_by_categories(skill_filter)


@skill_router.get(
    "/{skill_id}",
    response_model=SkillDetail,
    summary="Получить навык с этапами и вопросами этапа по id",
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_by_id(skill_id: int, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_skill(skill_id, current_user)
        skill = await SkillService(uow.session).get_skill_with_questions(skill_id)
        return skill


@skill_router.put(
    "/{skill_id}",
    response_model=SkillDetail,
    summary="Обновить навык по id с этапами и списком вопросов этапа",
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update(
    skill_id: int, skill: SkillUpdateForm, current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        new_skill = await SkillService(uow.session).update(skill_id, skill)
        return new_skill


@skill_router.delete("/{skill_id}", summary="Удалить навык по id")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def delete(skill_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await SkillService(uow.session).delete(skill_id)
        return {"detail": f"Навык с id = {skill_id} был удален."}
