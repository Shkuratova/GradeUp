from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import db_helper
from app.api.auth.schemas import (
    EmailModel,
    UserAuth,
    UserInfo,
    SUserRegistration,
    SUserAdd,
    SUserRole,
)
from app.api.auth import utils as auth_utils, tokens
from app.api.users.dao import UserDAO
from app.exceptions import (
    InvalidLoginException,
    UserAlreadyExistsException,
    UserNotFoundException,
    PasswordDontMatchException
)
from app.dependencies.auth_dependencies import (
    get_current_user,
    check_refresh_token,
    check_role_id,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/registration")
async def regiter_user(
    user_data: SUserRegistration,
    admin: UserInfo = Depends(check_role_id([3, 4])),
    session: AsyncSession = Depends(db_helper.session_with_commit),
) -> dict:
    user_dao = UserDAO(session=session)
    if user_exist := await user_dao.get_one_or_none(
        filter_by=EmailModel(email=user_data.email)
    ):
        raise UserAlreadyExistsException
    if user_data.password != user_data.confirm_password:
        raise PasswordDontMatchException
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
        raise InvalidLoginException
    if not auth_utils.validate_password(user_data.password, user.password):
        raise InvalidLoginException

    tokens.set_token(response=response, user=user, token_type="access_token")
    tokens.set_token(response=response, user=user, token_type="refresh_token")
    return {"detail": "Аутентификация прошла успешно"}


@router.post("/refresh")
def refresh_token(response: Response, user: UserInfo = Depends(check_refresh_token)):
    tokens.set_token(response=response, user=user, token_type="access_token")
    return {"detail": "Токен успешно обновлен"}


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Пользователь успешно вышел из системы"}


@router.get("/me", response_model=UserInfo)
def get_current_user(user: UserInfo = Depends(get_current_user)):
    return user


@router.post("/set-role")
async def set_user_role(
    user_data: SUserRole,
    admin: UserInfo = Depends(check_role_id([4])),
    session: AsyncSession = Depends(db_helper.session_with_commit),
) -> dict:
    user_dao = UserDAO(session=session)
    if not (
        existing_user := await user_dao.get_one_or_none_by_id(data_id=user_data.id)
    ):
        raise UserNotFoundException

    user_dict = user_data.model_dump()
    user_dict.drop("id")

    await user_dao.update_by_id(data_id=user_data.id, values=user_dict)
    return {"msg": f"Роль пользователя успешно обновлена"}
