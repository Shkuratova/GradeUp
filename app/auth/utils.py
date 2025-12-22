import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.auth.schemas import UserSchema


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
    encoded = jwt.encode(payload=payload, key=key, algorithm=algorithm)
    return encoded


def decode_jwt(token: str, algorithm=settings.jwt.algorithm):
    decoded = jwt.decode(token, algorithms=[algorithm])
    return decoded


def create_access_token(
    user: UserSchema,
    expire_minutes: int = settings.jwt.expire_access_token_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    token_data = {
        "sub": user.id,
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
    token_data = {"sub": user.id, "token_type": "refresh"}
    return encode_jwt(
        payload=token_data,
        expire_timedelta=timedelta(days=settings.jwt.expire_refresh_token_days),
    )


context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    return context.hash(password)


def validate_password(plain_password: str, hashed_password: str):
    return context.verify(plain_password, hashed_password)
