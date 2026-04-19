from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated
from schemas.users import (
    SUserFullInfo,
    SUserFilter,
    UserInfo,
    UserBase,
    UserUpdateBase,
    UserUpdateAdmin,
)
from dependencies import get_current_user, get_uow
from exceptions.user import ForbiddenException
from services.user import UserService
from db.uow import unit_of_work
from api.decorators import exception_handler, check_role
from api.roles import UserRole

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[SUserFullInfo], response_model_exclude_none=False)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all_users(
    user_filters: Annotated[SUserFilter, Query()],
    current_user: UserInfo = Depends(get_current_user),
) -> list[SUserFullInfo]:
    if current_user.role_name == UserRole.SUPERVISOR:
        if current_user.department_id is None:
            raise ForbiddenException("Руководитель не привязан к отделу.")
        user_filters.department_id = current_user.department_id
    async with unit_of_work() as uow:
        res = await UserService(uow.session).get_all(user_filters)
        return list(res)


@router.get("/{user_id}", response_model=UserInfo)
@exception_handler
async def get_user(
    user_id: int,
    current_user: UserInfo = Depends(get_current_user),
) -> UserInfo:
    async with unit_of_work() as uow:
        return await UserService(uow.session).get_user_role(UserBase(id=user_id))


@router.patch("/{user_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update_user(
    user_id: int,
    user_data: UserUpdateAdmin,
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        user_service = UserService(uow.session)
        if current_user.role_name == UserRole.ADMIN:
            await user_service.update_by_id(user_id, user_data)
        else:
            user_data = UserUpdateBase.model_validate(user_data.model_dump())
            await user_service.update_by_id(user_id, user_data)
        return {"detail": "Пользователь успешно обновлен"}
