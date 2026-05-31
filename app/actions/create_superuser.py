import sys
from pathlib import Path
import getpass
import asyncio
import logging

current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.insert(0, str(root_dir))

from db.uow import unit_of_work
from db.repository import UserRepository
from services import UserService
from schemas.users import UserAdd

logger = logging.getLogger(__name__)


async def create_superuser(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    patronymic: str | None = None,
):
    hashed_password = UserService.hash_password(password)

    superuser = UserAdd(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=hashed_password,
        role_id=3,
        patronymic=patronymic,
    )

    async with unit_of_work() as uow:
        user_repository = UserRepository(uow.session)
        existing_user = await user_repository.get_one_by_filter({"email": email})

        if existing_user:
            raise ValueError(f"Пользователь с email {email} уже существует.")

        await user_repository.add(superuser.model_dump(exclude_none=True))


def get_user_input():
    email = input("Enter email: ", ).strip()
    if not email:
        raise ValueError("Email is required")

    first_name = input("Enter first_name: ").strip().encode()
    if not first_name:
        raise ValueError("First name is required")

    last_name = input("Enter last_name: ").strip().encode()
    if not last_name:
        raise ValueError("Last name is required")

    patronymic = input("Enter patronymic (optional): ").strip().encode() or None

    password = getpass.getpass("Enter password: ").strip()
    if len(password) < 6:
        raise ValueError("Password length cannot be less than 6")

    confirm_password = getpass.getpass("Confirm password: ")
    if password != confirm_password:
        raise ValueError("Passwords don't match")

    return email, first_name, last_name, password, patronymic


async def main():
    try:
        email, first_name, last_name, password, patronymic = get_user_input()
        await create_superuser(email, first_name, last_name, password, patronymic)
        logger.info("Superuser with email=%s created successfully", email)
        print(f"Superuser {email} created successfully!")
    except ValueError as e:
        logger.error("Validation error: %s", e)
        print(f"Error: {e}")
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
