from fastapi import APIRouter, Depends, Response
from schemas.users import (
    UserAuth,
    UserInfo,
    UserRegistration,
)
from utils.auth import AuthUtils
from services import UserService
from db.uow import unit_of_work
from exceptions.user import PasswordDontMatchException
from api.decorators import exception_handler, check_role
from dependencies.auth import (
    get_current_user,
    check_refresh_token,
)
from api.roles import UserRole

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/registration")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def registration(
    user_data: UserRegistration,
    current_user: UserRole = Depends(get_current_user),
) -> dict:
    if user_data.password != user_data.confirm_password:
        raise PasswordDontMatchException
    async with unit_of_work() as uow:
        await UserService(uow.session).add(user_data)

    return {"detail": "Пользователь успешно добавлен"}


@auth_router.post("/login")
@exception_handler
async def login(
    response: Response,
    user_data: UserAuth,
) -> dict:
    async with unit_of_work() as uow:
        user_role = await UserService(uow.session).authenticate_user(user_data)
    AuthUtils.set_token(response=response, user=user_role, token_type="access_token")
    AuthUtils.set_token(response=response, user=user_role, token_type="refresh_token")
    return {"detail": "Аутентификация прошла успешно"}


@auth_router.post("/refresh")
def refresh_token(response: Response, user: UserInfo = Depends(check_refresh_token)):
    AuthUtils.set_token(response=response, user=user, token_type="access_token")
    return {"detail": "Токен успешно обновлен"}


@auth_router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Пользователь успешно вышел из системы"}


@auth_router.get("/me", response_model=UserInfo)
@exception_handler
async def get_current_user(user: UserInfo = Depends(get_current_user)):
    return user
