from fastapi import Request, Depends, HTTPException, status, Query
from jwt.exceptions import PyJWTError, ExpiredSignatureError

from db.uow import unit_of_work
from exceptions.user import (
    InvalidTokenException,
)
from schemas.users import UserBase, UserInfo, UserRoleName
from services.user import UserService
from utils import AuthUtils


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
        async with unit_of_work() as uow:
            user = await UserService(uow.session).get_user_role(UserBase(id=user_id))
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

def check_role(required_roles: list[UserRoleName]):

    async def checker(
        current_user: UserInfo = Depends(get_current_user)
    ):

        if current_user.role_name not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Отказано в доступе."
            )

        return current_user

    return checker