from fastapi import APIRouter, Depends, Response
from schemas.users import (
    UserAuth,
    UserInfo,
    UserRegistration,
    SetUserRole,
    UserRole,
)
from utils.auth import AuthUtils
from services import user_service
from exceptions.user import PasswordDontMatchException
from api.decorators import exception_handler, check_role
from dependencies.auth import (
    get_current_user,
    check_refresh_token,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/registration")
@check_role(["Admin", "Specialist"])
@exception_handler
async def registration(
    user_data: UserRegistration,
    current_user: UserRole = Depends(get_current_user),
) -> dict:
    if user_data.password != user_data.confirm_password:
        raise PasswordDontMatchException
    await user_service.add(user=user_data)

    return {"detail": "Пользователь успешно добавлен"}


@auth_router.post("/login")
@exception_handler
async def login(
    response: Response,
    user_data: UserAuth,
) -> dict:
    user_role = await user_service.authenticate_user(user_data)
    AuthUtils.set_token(response=response, user=user_role, token_type="access_token")
    AuthUtils.set_token(response=response, user=user_role, token_type="refresh_token")
    return {"detail": "Аутентификация прошла успешно"}


@auth_router.post("/refresh")
@exception_handler
def refresh_token(response: Response, user: UserInfo = Depends(check_refresh_token)):
    AuthUtils.set_token(response=response, user=user, token_type="access_token")
    return {"detail": "Токен успешно обновлен"}


@auth_router.post("/logout")
@exception_handler
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Пользователь успешно вышел из системы"}


@auth_router.get("/me", response_model=UserInfo)
async def get_current_user(user: UserInfo = Depends(get_current_user)):
    return user


@auth_router.post("/set-role")
@check_role(["Admin"])
@exception_handler
async def set_user_role(
    user_data: SetUserRole, current_user: UserRole = Depends(get_current_user)
) -> dict:
    await user_service.update_by_id(user_data.id, user_data)
    return {"detail": f"Роль пользователя успешно обновлена"}
