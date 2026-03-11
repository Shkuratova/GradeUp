from fastapi import  APIRouter, Depends, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import SUserFullInfo, SUserFilter, UserInfo
from dependencies.auth import check_role, get_current_user
from exceptions.user import ForbiddenException, UserNotFoundException
from services.user import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[SUserFullInfo], response_model_exclude_none=True)
async def get_all_users(
        user_filters: Annotated[SUserFilter, Query()],
        user_data: UserInfo = Depends(check_role(["Admin", "Specialist", "Supervisor"])),
) -> list[SUserFullInfo]:
    if user_data.role_name == "Supervisor":
        if user_data.department_id is None:
            raise ForbiddenException
        user_filters.department_id = user_data.department_id
    res = await user_service.get_all(user_filters)
    return list(res)


@router.get("/{user_id}", response_model=SUserFullInfo)
async def get_user_by_id(
            user_id: int,
            user_data: UserInfo = Depends(get_current_user),
            )-> SUserFullInfo:
    pass