from typing import Annotated
from fastapi import APIRouter, Depends, Query
from dependencies.auth import get_current_user
from api.decorators import check_role, exception_handler
from services.access import AccessService
from utils.roles import UserRole
from db.uow import unit_of_work
from services.profile import ProfileService
from schemas.users import UserInfo
from schemas.profiles import (
    SProfileAdd,
    SProfileUpdate,
    ProfileList,
    ProfileDetail,
    ProfileFilter, ProfileStructure,
)

profile_router = APIRouter(prefix="/profiles", tags=["Profiles"])


@profile_router.get(
    "/",
    response_model=list[ProfileList],
    summary="Получить список профилей",
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(
    filters: Annotated[ProfileFilter, Query()],
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        filters.departments_id = await AccessService(uow.session).get_department_filter(
            current_user,
            filters.departments_id,
        )
        return await ProfileService(uow.session).get_profile_list(filters)


@profile_router.post("/", summary="Создать профиль с уровнями и навыками")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(profile: SProfileAdd, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:

        return await ProfileService(uow.session).add_profile(profile)


@profile_router.get("/levels", summary="Получить список профилей с уровнями и навыками")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_profiles_with_levels(
    filters: Annotated[ProfileFilter, Query()], current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        filters.departments_id = await AccessService(uow.session).get_department_filter(
            current_user, filters.departments_id
        )
        return await ProfileService(uow.session).get_profile_levels(filters)


@profile_router.get(
    "/{profile_id}",
    response_model=ProfileDetail,
    summary="Получить профиль с уровнями и списком нвыков по id",
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_by_id(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_profile(profile_id, current_user)
        return await ProfileService(uow.session).get_with_details(profile_id)


@profile_router.put(
    "/{profile_id}",
    response_model=ProfileDetail,
    summary="Обновления профиля с уровнями и списком навыков",
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update_by_id(
    profile_id: int, profile: SProfileUpdate, current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).update_by_id(profile_id, profile)


@profile_router.delete("/{profile_id}", summary="Удалить профиль по id")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def delete_by_id(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await ProfileService(uow.session).soft_delete_by_id(profile_id)
    return {f"Профиль c id = {profile_id} был удален."}


@profile_router.get(
    "/{profile_id}/structure",
    response_model=ProfileStructure,
    summary="Получить полную структуру профиля по id"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_by_id(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_profile(profile_id, current_user)
        return await ProfileService(uow.session).get_structure(profile_id)
