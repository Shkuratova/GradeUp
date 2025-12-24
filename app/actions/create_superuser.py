from sqlalchemy import insert
import asyncio
from os import getenv
from app.auth import User
import app.auth.utils as auth_utils
from app.db import db_helper


default_email = getenv("DEFAULT_EMAIL", "admin@example.com")
default_password = getenv("DEFAULT_PASSWORD", "admin")
default_role_id = 4


async def create_superuser():
    stmt = insert(User).values(
        email=default_email,
        role_id=default_role_id,
        password=auth_utils.hash_password(default_password),
    )
    async with db_helper.session_maker() as session:
        try:
            await session.execute(stmt)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_superuser())