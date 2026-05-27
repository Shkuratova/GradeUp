from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from dependencies import get_current_user
from schemas.users import (
    UserFilter,
    UserInfo,
    UserUpdateAdmin, ResetPassword,
)
from services import DepartmentService, EventService, AccessService, UserService
from utils.roles import UserRole

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "/", response_model=list[UserInfo], summary="Получить список пользователей"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(
    filters: Annotated[UserFilter, Query()],
    current_user: UserInfo = Depends(get_current_user),
) -> list[UserInfo]:
    async with unit_of_work() as uow:
        auth_service = AccessService(uow.session)
        if filters.division_id:
            filters.departments_id = await DepartmentService(
                uow.session
            ).get_id_by_division(filters.division_id)

        filters.departments_id = await auth_service.get_department_filter(
            current_user, filters.departments_id
        )
        if filters.only_subordinates:
            filters.departments_id = await auth_service.get_managed_departments(
                current_user
            )

        res = await UserService(uow.session).get_users(filters)
        return list(res)


@user_router.patch("/reset-password", summary="Сбросить пароль", tags=["Auth"])
@check_role([UserRole.ADMIN])
@exception_handler
async def reset_password(user_id: int, reset_form: ResetPassword, current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        await UserService(uow.session).reset_password(user_id, reset_form)
        return {"detail": "Пароль успешно обновлён"}


user_detail_router = APIRouter(prefix="/{user_id}", tags=["Users", "UserDetail"])


@user_detail_router.get(
    "/", response_model=UserInfo, summary="Получить пользователя по id"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_by_id(
    user_id: int, current_user: UserInfo = Depends(get_current_user)
) -> UserInfo:
    async with unit_of_work() as uow:
        await AccessService(uow.session).can_get_user(user_id, current_user)
        return await UserService(uow.session).get_user_info(user_id=user_id)


@user_detail_router.patch(
    "/", response_model=UserInfo, summary="Обновить даннные пользователя по id"
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update_user(
    user_id: int,
    user_data: UserUpdateAdmin,
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        user_service = UserService(uow.session)
        upd, old = await user_service.update(user_id, user_data, current_user)
        if upd.role_id != old.role_id:
            await EventService(uow.session).log_set_user_role(
                old.role, upd, current_user
            )
        return upd

