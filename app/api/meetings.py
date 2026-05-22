from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from dependencies import get_current_user
from schemas.meetings import (
    MeetingAddForm,
    MeetingFilters,
    MeetingDetail,
    MeetingUpdateForm,
)
from schemas.users import (
    UserInfo,
)
from services.meetings import MeetingService
from utils.roles import UserRole

meeting_router = APIRouter(prefix="/meetings", tags=["Meetings"])


@meeting_router.get("/", response_model=list[MeetingDetail])
@exception_handler
async def get_all(
    filters: Annotated[MeetingFilters, Query()], current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:

        return await MeetingService(uow.session).get_meetings(filters)


@meeting_router.post("/", response_model=MeetingDetail)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def add(
    meeting: MeetingAddForm, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        return await MeetingService(uow.session).schedule_meeting(meeting, current_user)


@meeting_router.get("/next")
@exception_handler
async def get_user_next_meeting(current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await MeetingService(uow.session).get_user_next_meeting(current_user.id)


@meeting_router.put("/{meeting_id}", response_model=MeetingDetail)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def update(
    meeting_id: int, meeting: MeetingUpdateForm, current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        return await MeetingService(uow.session).update_meeting(
            meeting_id, meeting, current_user
        )


@meeting_router.delete("/{meeting_id}")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def delete(meeting_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        res = await MeetingService(uow.session).delete_by_id(meeting_id)
        return {"detail": f"Встреча с id = {meeting_id} была удалена."}


@meeting_router.get("/{meeting_id}/questions")
@exception_handler
async def get_questions(
    meeting_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        return await MeetingService(uow.session).get_questions(meeting_id, current_user)
