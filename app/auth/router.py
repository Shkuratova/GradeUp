from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import db_helper
from .schemas import EmailModel, UserAuth, UserInfo, SUserRegistration, SUserAdd, SUserRole, SUserFullInfo
import app.auth.utils as auth_utils
from app.auth.tokens import set_token
from .dao import UserDAO
from app.exceptions import InvalidLogin, UserAlreadyExistsException, UserNotFoundException
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
    admin: UserInfo = Depends(check_role_id([2, 3, 4])),
    session: AsyncSession = Depends(db_helper.session_without_commit),
) -> list[SUserFullInfo]:
    res = await UserDAO(session=session).get_user_list_by_role(admin)
    return list(res)


@router.post("/set-role/{user_id}")
async def set_user_role(
    user_id: int, 
    user_role_id: SUserRole, 
    admin: UserInfo = Depends(check_role_id([4])),
    session: AsyncSession = Depends(db_helper.session_with_commit),
) -> dict:
    user_dao = UserDAO(session=session)
    if not (existing_user := await user_dao.get_one_or_none_by_id(data_id=user_id)):
        raise UserNotFoundException
    await user_dao.update_by_id(data_id=user_id, values=user_role_id.model_dump())
    return {"msg": f"Роль пользователя успешно обновлена"}
