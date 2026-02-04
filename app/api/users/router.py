from fastapi import  APIRouter, Depends, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import  AsyncSession

from app.db import  db_helper
from app.api.users import SUserFullInfo, SUserFilter, UserDAO
from app.api.auth.schemas import  UserInfo
from app.dependencies.auth_dependencies import check_role_id
from app.exceptions import ForbiddenException


router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("/", response_model=list[SUserFullInfo], response_model_exclude_none=True)
async def get_all_users(
        user_filters: Annotated[SUserFilter, Query()],
        user_data: UserInfo = Depends(check_role_id([2, 3, 4])),
        session: AsyncSession = Depends(db_helper.session_without_commit),
) -> list[SUserFullInfo]:
    if user_data.role_id == 2:
        if user_data.department_id is None:
            raise ForbiddenException
        user_filters.department_id = user_data.department_id

    res = await UserDAO(session=session).get_user_list(user_filters)
    return list(res)