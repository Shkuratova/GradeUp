from typing import Annotated

from fastapi import APIRouter, Depends, Query
from db.models.events import EventType, TargetType
from dependencies import get_current_user
from api.decorators import exception_handler, check_role
from schemas.event import EventFilter, EventSchema
from services.access import AccessService
from services.event import EventService
from utils.roles import UserRole
from db.repository import RoleRepository
from db.uow import unit_of_work

from schemas.users import UserInfo, SRole

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.get(
    "/roles",
    response_model=list[SRole],
    summary="Список доступных ролей для назначения",
)
@check_role([UserRole.ADMIN])
@exception_handler
async def get_roles(current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        roles = await RoleRepository(uow.session).get_all()
        return roles


@admin_router.get("/event-types")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_event_types(current_user: UserInfo = Depends(get_current_user)):
    return {i: v for i, v in enumerate(list(EventType))}


@admin_router.get("/event-target")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_event_target(current_user: UserInfo = Depends(get_current_user)):
    return {i: v for i, v in enumerate(list(TargetType))}


@admin_router.get("/events", response_model=list[EventSchema], summary="Журнал событий")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_events(
    filters: Annotated[EventFilter, Query()],
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        AccessService.get_accessible_event_types(filters.event_type, current_user)
        return await EventService(uow.session).get_events(filters)
