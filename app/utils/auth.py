from fastapi import Response
import jwt
from datetime import datetime, timedelta, timezone
from config import settings
from schemas.users import UserRole, UserInfo

class AuthUtils:
    @staticmethod
    def encode_jwt(
        payload: dict,
        key: str = settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
        expire_minutes: int = settings.jwt.expire_access_token_minutes,
        expire_timedelta: timedelta | None = None,
    ) -> str:
        to_encode = payload.copy()
        now = datetime.now(tz=timezone.utc)

        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=expire_minutes)

        to_encode.update(exp=expire, iat=now)
        encoded = jwt.encode(payload=to_encode, key=key, algorithm=algorithm)
        return encoded

    @staticmethod
    def decode_jwt(
        token: str, key=settings.jwt.secret_key, algorithm=settings.jwt.algorithm
    ):
        decoded = jwt.decode(token, key=key, algorithms=[algorithm])
        return decoded

    @classmethod
    def create_access_token(
        cls,
        user: UserInfo,
        expire_minutes: int = settings.jwt.expire_access_token_minutes,
        expire_timedelta: timedelta | None = None,
    ) -> str:
        token_data = {
            "sub": str(user.id),
            "role": user.role_name,
            "token_type": "access",
        }
        return cls.encode_jwt(
            payload=token_data,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
        )

    @classmethod
    def create_refresh_token(cls, user: UserInfo) -> str:
        token_data = {"sub": str(user.id), "token_type": "refresh"}
        return cls.encode_jwt(
            payload=token_data,
            expire_timedelta=timedelta(days=settings.jwt.expire_refresh_token_days),
        )

    @classmethod
    def set_token(
        cls, response: Response, user: UserInfo, token_type: str = "access_token"
    ):
        if token_type == "access_token":
            token = cls.create_access_token(user)
        else:
            token = cls.create_refresh_token(user)
        response.set_cookie(
            key=token_type, value=token, httponly=True, secure=True, samesite="lax"
        )
