from fastapi import APIRouter, Depends, Query
from typing import Annotated
from dependencies.auth import get_current_user
from services.questions import QuestionService
from services.skill import SkillService
from db.uow import unit_of_work
from schemas.questions import SQuestion, QuestionFilter, QuestionAdd, QuestionUpdate
from api.decorators import exception_handler, check_role
from api.roles import UserRole
from schemas.questions import QuestionFilter

question_router = APIRouter(prefix="/questions", tags=["Questions"])


@question_router.get(
    "/", response_model=list[SQuestion]
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(
    filters: Annotated[QuestionFilter, Query()],
        current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        return await QuestionService(uow.session).get_all(filters)


# list
@question_router.post("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(
        questions: list[QuestionAdd],
        current_user = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await QuestionService(uow.session).add(questions)


# list
@question_router.patch("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update(questions: list[QuestionUpdate],
                 current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        updated, added = await QuestionService(uow.session).update(questions)
        return {"detail": f"Обновлено записей: {updated}, добавлено записей: {added}"}

