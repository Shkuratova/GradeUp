from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import db_helper
from app.auth.dao import UserDAO
from app.auth.schemas import EmailModel, UserAuth
from app.auth import utils
from app.exceptions import InvalidLogin, InvalidToken

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login_user(
    user_data: UserAuth,
    session: AsyncSession = Depends(db_helper.session_without_commit),
) -> dict:
    user_dao = UserDAO(session=session)
    user = await user_dao.get_one_or_none(filter_by=EmailModel(email=user_data.email))
    if not user:
        raise InvalidLogin
    if not utils.validate_password(user_data.password, user.password):
        raise InvalidLogin

    return {
        "access_token": utils.create_access_token(user),
        "refresh_token": utils.create_refresh_token(user),
    }
