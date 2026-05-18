from typing import Annotated
from fastapi import APIRouter, Depends, Query
from dependencies.auth import get_current_user
from api.decorators import check_role, exception_handler
from services import DepartmentService
from utils.roles import UserRole
from db.uow import unit_of_work
from services.profile import ProfileService
from schemas.users import UserInfo
from schemas.profiles import (
    SProfileAdd,
    SProfileUpdate,
    ProfileList,
    ProfileDetail,
    ProfileFilter,
)

profile_router = APIRouter(prefix="/profiles", tags=["Profiles"])


@profile_router.get("", response_model=list[ProfileList])
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(
    profile_filter: Annotated[ProfileFilter, Query()],
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        department_ids = await DepartmentService(
            uow.session
        ).get_accessible_departments(current_user, profile_filter.department_id)
        return await ProfileService(uow.session).get_profile_list(
            profile_filter, department_ids
        )


@profile_router.post("")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(profile: SProfileAdd, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).add_profile(profile)


@profile_router.get("/levels", response_model=list[ProfileDetail])
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_levels(
    profile_filter: Annotated[ProfileFilter, Query()],
    current_user=Depends(get_current_user),
):
    async with unit_of_work() as uow:
        department_ids = await DepartmentService(
            uow.session
        ).get_accessible_departments(current_user, profile_filter.department_id)
        profiles = await ProfileService(uow.session).get_profile_levels(
             department_ids=department_ids
        )
        return profiles


@profile_router.get(
    "/{profile_id}"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_by_id(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        department_ids = await DepartmentService(
            uow.session
        ).get_accessible_departments(current_user)
        return await ProfileService(uow.session).get_with_details(
            profile_id, department_ids
        )


@profile_router.put("/{profile_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update_by_id(
    profile_id: int, profile: SProfileUpdate, current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await ProfileService(uow.session).update_by_id(profile_id, profile)
    return {"detail": "Профиль успешно обновлен."}


@profile_router.delete("/{profile_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def delete_by_id(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await ProfileService(uow.session).soft_delete_by_id(profile_id)
    return {f"Профиль c id = {profile_id} был удален."}
