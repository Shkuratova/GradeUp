import logging
from typing import Annotated

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, Query

from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from dependencies import get_current_user
from schemas.meetings import (
    MeetingAddForm,
    MeetingFilters,
    MeetingDetail,
    MeetingUpdateForm,
    MeetingQuestions,
)
from schemas.users import (
    UserInfo,
)
from services import MeetingService, EventService, AccessService
from utils.roles import UserRole

meeting_router = APIRouter(prefix="/meetings", tags=["Meetings"])


@meeting_router.get(
    "/", response_model=list[MeetingDetail], summary="Получить список встреч"
)
@exception_handler
async def get_all(
    filters: Annotated[MeetingFilters, Query()], current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        filters = await AccessService(uow.session).get_meeting_filter(filters, current_user)
        return await MeetingService(uow.session).get_meetings(filters)


@meeting_router.post("/", response_model=MeetingDetail, summary="Назначить встречу")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def add(
    meeting: MeetingAddForm, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        new_meeting = await MeetingService(uow.session).schedule_meeting(
            meeting, current_user
        )
        await EventService(uow.session).log_schedule(new_meeting, current_user)
        return new_meeting


@meeting_router.get("/next", summary="Получить ближайшую встречу текущего пользователя")
@exception_handler
async def get_user_next_meeting(current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await MeetingService(uow.session).get_user_next_meeting(current_user.id)


@meeting_router.get(
    "/{meeting_id}", response_model=MeetingDetail, summary="Получить встречу по id"
)
@exception_handler
async def get_by_id(meeting_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await MeetingService(uow.session).get_meeting_by_id(meeting_id)


@meeting_router.put(
    "/{meeting_id}", response_model=MeetingDetail, summary="Обновить встречу по id"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def update(
    meeting_id: int, meeting: MeetingUpdateForm, current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_manage_meeting(meeting_id, current_user)
        upd = await MeetingService(uow.session).update_meeting(
            meeting_id, meeting, current_user
        )
        await EventService(uow.session).log_meeting_changed(upd, current_user)
        return upd


@meeting_router.delete("/{meeting_id}", summary="Удалить встречу")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def delete(meeting_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_manage_meeting(meeting_id, current_user)
        await MeetingService(uow.session).delete_by_id(meeting_id)
        return {"detail": f"Встреча с id = {meeting_id} была удалена."}


@meeting_router.get(
    "/{meeting_id}/materials",
    response_model=MeetingQuestions,
    response_model_exclude_none=True,
    summary="Получить список материалов встречи",
)
@exception_handler
async def get_questions(
    meeting_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        return await MeetingService(uow.session).get_questions(meeting_id, current_user)
