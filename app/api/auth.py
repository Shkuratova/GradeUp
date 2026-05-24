from fastapi import APIRouter, Depends, Response
from dependencies.auth import (
    get_current_user,
    check_refresh_token,
)
from utils.auth import AuthUtils
from utils.roles import UserRole
from api.decorators import exception_handler, check_role
from db.uow import unit_of_work
from services import UserService, EventService
from schemas.users import (
    UserAuth,
    UserInfo,
    UserRegistration,
    UserBase,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/registration",
    response_model=UserInfo,
    summary="Регистрация нового пользователя (Только для Администраторов и СПО.",
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def registration(
    user_data: UserRegistration,
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        user_service = UserService(uow.session)
        new_user = await user_service.add(user_data)
        new_user = await user_service.get_user_role(UserBase(id=new_user.id))
        await EventService(uow.session).log_registration(
            user=new_user, current_user=current_user
        )
        return new_user


@auth_router.post("/login", summary="Вход в систему")
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


@auth_router.post("/refresh", summary="Обновление токена доступа")
def refresh_token(response: Response, user: UserInfo = Depends(check_refresh_token)):
    AuthUtils.set_token(response=response, user=user, token_type="access_token")
    return {"detail": "Токен успешно обновлен"}


@auth_router.post("/logout", summary="Выход из системы")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Пользователь успешно вышел из системы"}


@auth_router.get(
    "/me", response_model=UserInfo, summary="Получение текущего пользователя из токена"
)
@exception_handler
async def get_current_user(user: UserInfo = Depends(get_current_user)):
    return user
