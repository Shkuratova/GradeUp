from fastapi import Response
from app.auth.utils import encode_jwt, decode_jwt
from app.auth.schemas import UserSchema
from datetime import datetime, timezone, timedelta
from app.config import settings

def create_access_token(
    user: UserSchema,
    expire_minutes: int = settings.jwt.expire_access_token_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role_id": user.role_id,
        "token_type": "access",
    }
    return encode_jwt(
        payload=token_data,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_refresh_token(user: UserSchema) -> str:
    token_data = {"sub": str(user.id), "token_type": "refresh"}
    return encode_jwt(
        payload=token_data,
        expire_timedelta=timedelta(days=settings.jwt.expire_refresh_token_days),
    )


def set_token(response: Response, user: UserSchema, token_type:str = "access_token"):
    if token_type == "access_token":
        token = create_access_token(user)
    else:
        token = create_refresh_token(user)
    response.set_cookie(
        key=token_type,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax"
    )

