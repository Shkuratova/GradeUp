import sys
from pathlib import Path

current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.insert(0, str(root_dir))

import asyncio
from os import getenv
from db.uow import unit_of_work
from db.repository import UserRepository
from services import UserService

default_email = getenv("DEFAULT_EMAIL", "admin@example.com")
default_password = getenv("DEFAULT_PASSWORD", "admin")


async def create_superuser():
    admin = {
        "email": default_email,
        "first_name": "admin",
        "last_name": "admin",
        "password": UserService.hash_password(default_password),
        "role_id": 3,
        "position": "Администратор",
        "patronymic": None,
    }

    async with unit_of_work() as uow:

        await UserRepository(uow.session).add(admin)


if __name__ == "__main__":
    asyncio.run(create_superuser())
