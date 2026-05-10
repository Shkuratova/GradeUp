from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from api.decorators import check_role, exception_handler
from utils.roles import UserRole
from db.uow import unit_of_work
from services.skill import StageService
from schemas.users import UserInfo
from schemas.skills import StageAdd, StageQuestionsSchema

stage_router = APIRouter(prefix="/stages", tags=["Skill"])


@stage_router.put("/{stage_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update(stage_id:int, stage: StageAdd, current_user: UserInfo=Depends(get_current_user)):
    async with unit_of_work() as uow:
        res = await StageService(uow.session).update_questions(stage_id, stage)
        return res

@stage_router.get("/{stage_id}", response_model=StageQuestionsSchema)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_stage_questions(stage_id: int, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        res = await StageService(uow.session).get_questions(stage_id)
        return res
