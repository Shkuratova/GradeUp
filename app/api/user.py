from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated

from fastapi.exceptions import ValidationException
from schemas.users import (
    SUserFullInfo,
    SUserFilter,
    UserInfo,
    UserBase,
    UserUpdateBase,
    UserUpdateSupervisor,
    UserUpdateAdmin,
)
from dependencies.auth import get_current_user
from exceptions.user import ForbiddenException
from services.user import user_service
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
    res = await user_service.get_all(user_filters)
    return list(res)


@router.get("/{user_id}", response_model=UserInfo)
@exception_handler
async def get_user(
    user_id: int,
    current_user: UserInfo = Depends(get_current_user),
) -> UserInfo:
    return await user_service.get_user_role(user_id)


@router.patch("/{user_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update_user(
    user_id: int,
    user_data: UserUpdateAdmin,
    current_user: UserInfo = Depends(get_current_user),
):
    if current_user.role_name == UserRole.ADMIN:
        await user_service.update_by_id(user_id, user_data)
    else:
        user_data = UserUpdateBase.model_validate(user_data.model_dump())
        await user_service.update_by_id(user_id, user_data)
    return {"detail": "Пользователь успешно обновлен"}
