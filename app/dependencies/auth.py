from fastapi import Request, Depends, HTTPException, status
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from schemas.users import UserBase, UserRole, UserInfo
from exceptions.user import (
    InvalidTokenException,
)
from utils import AuthUtils
from services.user import user_service


def get_token_by_type(token_type: str):
    def get_token(request: Request) -> str:
        token = request.cookies.get(token_type)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен отсутствует.")
        return token

    return get_token


async def get_user_from_token(token: str)-> UserInfo:
    try:
        payload = AuthUtils.decode_jwt(token=token)
        if not (user_id := payload.get("sub")) or not (role := payload.get("role")):
            raise InvalidTokenException("Некорректный токен.")
        user = await user_service.get_user_role(UserBase(id=user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")
        return UserInfo.model_validate(user)
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек.")
    except PyJWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))


async def check_refresh_token(
    token: str = Depends(get_token_by_type("refresh_token")),
) -> UserInfo:
    return await get_user_from_token(token=token)


async def get_current_user(
    token: str = Depends(get_token_by_type("access_token")),
) -> UserInfo:
    return await get_user_from_token(token=token)
