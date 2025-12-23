from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import db_helper
from .schemas import EmailModel, UserAuth, UserInfo
import app.auth.utils as auth_utils
from .dao import UserDAO
from app.exceptions import InvalidLogin, InvalidToken
from app.auth.dependencies import get_current_user, check_refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])


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

    auth_utils.set_token(response=response, user=user, token_type="access_token")
    auth_utils.set_token(response=response, user=user, token_type="refresh_token")
    return {"detail": "Аутентификация прошла успешно"}


@router.post("/refresh")
def refresh_token(
    response: Response, 
    user: UserInfo = Depends(check_refresh_token)
):
    auth_utils.set_token(response=response, user=user, token_type="access_token")
    return {"detail": "Токен успешно обновлен"}


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Пользователь успешно вышел из системы"}

@router.get("/me", response_model=UserInfo)
def get_current_user(user: UserInfo = Depends(get_current_user)):
    return user


