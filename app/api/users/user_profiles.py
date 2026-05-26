from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from dependencies import get_current_user
from schemas.user_profile import (
    UserProfileAdd,
    UserProfileFilter,
    UserProfileSchema,
    UserProgressList,
)
from schemas.user_progress import ProfileProgress
from schemas.users import UserInfo
from services import (
    AccessService,
    EventService,
    UserProfileService,
    UserProgressService,
)
from utils.roles import UserRole

user_profile_router = APIRouter(
    prefix="/users/profiles", tags=["Users", "UserProfiles"]
)


@user_profile_router.get(
    "/",
    response_model=list[UserProgressList],
    summary="Получить список пользователей с назначенными профилями и прогрессом по уровням",
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(
    filters: Annotated[UserProfileFilter, Query()],
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        filters.departments_id = await AccessService(uow.session).get_department_filter(
            current_user, filters.departments_id
        )
        return await UserProfileService(uow.session).get_all_with_progress(filters)


@user_profile_router.post(
    "/", response_model=UserProfileSchema, summary="Назначить профиль пользователю"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def add(
    user_profile: UserProfileAdd, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        access_service = AccessService(uow.session)
        await access_service.can_manage_user(user_profile.user_id, current_user)
        await access_service.can_get_profile(user_profile.profile_id, current_user)

        new_user_profile = await UserProfileService(uow.session).create(user_profile)
        await EventService(uow.session).log_set_user_profile(
            new_user_profile, current_user
        )
        return new_user_profile


user_profile_detail_router = APIRouter(prefix="/profile", tags=["UserProfileProgress"])


@user_profile_detail_router.get(
    "/",
    response_model=ProfileProgress,
    summary="Получить прогресс по профилю пользователя",
)
@exception_handler
async def get_by_id(user_id: int, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_user_profile(user_id, current_user)
        return await UserProgressService(uow.session).get_profile_progress(user_id)


@user_profile_detail_router.delete("", summary="Открепить профиль от пользователя")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def delete_by_id(user_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_user_profile(user_id, current_user)
        await UserProfileService(uow.session).delete(user_id)
    return {"detail": "Профиль откреплен от пользователя."}


@user_profile_detail_router.post(
    "/grade-up", summary="Повысить уровень профиля пользователя"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def gradeup_user(
    user_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_user_profile(user_id, current_user)
        res = await UserProfileService(uow.session).gradeup(user_id)
        await EventService(uow.session).log_gradeup(user_id, res, current_user)
        return res
