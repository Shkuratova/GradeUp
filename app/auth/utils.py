import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.config import settings

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


def decode_jwt(token: str, key=settings.jwt.secret_key, algorithm=settings.jwt.algorithm):
    decoded = jwt.decode(token, key=key, algorithms=[algorithm])
    return decoded


context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    return context.hash(password)


def validate_password(plain_password: str, hashed_password: str):
    return context.verify(plain_password, hashed_password)
