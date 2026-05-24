from fastapi import APIRouter, Depends

from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from dependencies import get_current_user
from schemas.user_profile import UserStageAdd
from schemas.users import UserInfo
from services import AccessService, EventService
from services.user_stage import UserStageService
from utils.roles import UserRole

evaluation_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@evaluation_router.post("/", summary="Оценить этап пользователя")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def evaluate(user_stage: UserStageAdd, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_manage_user(user_stage.user_id, current_user)
        evaluation =  await UserStageService(uow.session).evaluate(user_stage)
        await EventService.log_evaluate_stage(user_stage, current_user)
        return evaluation


@evaluation_router.get("/{user_stage_id}", summary="Получить оценку этапа пользователя")
@exception_handler
async def get(user_stage_id: int, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        pass
