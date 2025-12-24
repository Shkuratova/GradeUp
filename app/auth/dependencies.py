from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from app.exceptions import TokenNotFound, InvalidToken, TokenExpired, ForbiddenException
from app.db import db_helper
from app.auth import UserDAO, User, auth_utils


def get_access_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise TokenNotFound
    return token


def get_refresh_token(request: Request) -> str:
    token = request.cookies.get("refresh_token")
    if not token:
        raise TokenNotFound
    return token


async def get_user_from_token(token: str, session: AsyncSession) -> User:
    try:
        payload = auth_utils.decode_jwt(token=token)
        if not (user_id := payload.get("sub")):
            raise InvalidToken
        user = await UserDAO(session=session).get_one_or_none_by_id(
            data_id=int(user_id)
        )
        if not user:
            raise InvalidToken
        return user
    except ExpiredSignatureError as e:
        raise TokenExpired
    except PyJWTError as e:
        raise InvalidToken


async def check_refresh_token(
    token: str = Depends(get_refresh_token),
    session: AsyncSession = Depends(db_helper.session_without_commit),
) -> User:
    return await get_user_from_token(token=token, session=session)


async def get_current_user(
    token: str = Depends(get_access_token),
    session: AsyncSession = Depends(db_helper.session_without_commit),
) -> User:
    return await get_user_from_token(token=token, session=session)


def check_role_id(roles: list[int]):
    def get_current_user_role(user: User = Depends(get_current_user)):
        if user.role_id not in roles:
            raise ForbiddenException
        return user
    return get_current_user_role