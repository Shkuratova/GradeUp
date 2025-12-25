from typing import Annotated
from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import db_helper
from .schemas import (
    EmailModel, 
    UserAuth, 
    UserInfo, 
    SUserRegistration, 
    SUserAdd, 
    SUserRole, 
    SUserFullInfo,
    SUserFilter
    )
import app.auth.utils as auth_utils
from app.auth.tokens import set_token
from .dao import UserDAO
from app.exceptions import InvalidLogin, UserAlreadyExistsException, UserNotFoundException, ForbiddenException
from app.auth.dependencies import get_current_user, check_refresh_token, check_role_id

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/registration")
async def regiter_user(
    user_data: SUserRegistration,
    admin: UserInfo = Depends(check_role_id([3, 4])),
    session: AsyncSession = Depends(db_helper.session_with_commit),
) -> dict:
    print("eee", user_data)
    user_dao = UserDAO(session=session)
    if user_exist := await user_dao.get_one_or_none(
        filter_by=EmailModel(email=user_data.email)
    ):
        raise UserAlreadyExistsException

    user_dict = user_data.model_dump()
    await user_dao.add(values=SUserAdd(**user_dict))

    return {"detail": "Пользователь успешно добавлен"}


@router.post("/login")
async def login_user(
    response: Response,
    user_data: UserAuth,
    session: AsyncSession = Depends(db_helper.session_without_commit),
) -> dict:
    user_dao = UserDAO(session=session)
    user = await user_dao.get_one_or_none(filter_by=EmailModel(email=user_data.email))
    if not user:
        raise InvalidLogin
    if not auth_utils.validate_password(user_data.password, user.password):
        raise InvalidLogin

    set_token(response=response, user=user, token_type="access_token")
    set_token(response=response, user=user, token_type="refresh_token")
    return {"detail": "Аутентификация прошла успешно"}


@router.post("/refresh")
def refresh_token(response: Response, user: UserInfo = Depends(check_refresh_token)):
    set_token(response=response, user=user, token_type="access_token")
    return {"detail": "Токен успешно обновлен"}


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Пользователь успешно вышел из системы"}


@router.get("/me", response_model=UserInfo)
def get_current_user(user: UserInfo = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[SUserFullInfo], response_model_exclude_none=True)
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


@router.post("/set-role")
async def set_user_role(
    user_data: SUserRole, 
    admin: UserInfo = Depends(check_role_id([4])),
    session: AsyncSession = Depends(db_helper.session_with_commit),
) -> dict:
    user_dao = UserDAO(session=session)
    if not (existing_user := await user_dao.get_one_or_none_by_id(data_id=user_data.id)):
        raise UserNotFoundException
    
    user_dict = user_data.model_dump()
    user_dict.drop("id")

    await user_dao.update_by_id(data_id=user_data.id, values=user_dict)
    return {"msg": f"Роль пользователя успешно обновлена"}
