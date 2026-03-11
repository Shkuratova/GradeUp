from pydantic import BaseModel

from schemas.users import UserAdd, UserInfo
from db.uow import unit_of_work
from db.repository.user import user_repository_factory, UserRepository
import bcrypt
from schemas.users import UserAuth, UserRole, EmailModel, SUser
from exceptions.user import (
    UserNotFoundException,
    UserAlreadyExistException,
    InvalidLoginException,
)

class UserService:

    def __init__(self, repository_factory):
        self.repository_factory = repository_factory

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def validate_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    async def add(self, user: UserAdd):
        async with unit_of_work() as uow:
            repository = self.repository_factory(uow.session)
            user_exist = await repository.get_one_by_filter({"email": user.email})
        if user_exist is not None:
            raise UserAlreadyExistException(
                f"Пользователь с почтой {user.email} уже существует."
            )
        user.password = self.hash_password(user.password)
        async with unit_of_work() as uow:
            repository = self.repository_factory(uow.session)
            return await repository.add(user.model_dump(exclude_none=True))

    async def get_all(self, filter_model: BaseModel):
        filter_dict = filter_model.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            repository = self.repository_factory(uow.session)
            users =  await repository.get_all(filter_dict)
            print(users)
            return users

    async def get_by_id(self, user_id: int) -> SUser:
        async with unit_of_work() as uow:
            repository = self.repository_factory(uow.session)
            user = await repository.get_by_id(user_id)
            if user is None:
                raise UserNotFoundException("Пользователь не найден")
            return SUser.model_validate(user)

    async def get_user_role(self, user_filter: BaseModel) -> UserRole:
        filter_dict = user_filter.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            user_repository = self.repository_factory(uow.session)
            user = await user_repository.get_user_role(filter_dict)
            return user

    async def update_by_id(self, user_id: int, user: BaseModel):
        async with unit_of_work() as uow:
            repository: UserRepository = self.repository_factory(uow.session)
            user_dict = user.model_dump(exclude_none=True)
            res = await repository.update_by_id(user_id, user_dict)
            if not res:
                raise UserNotFoundException("Пользователь не найден.")


    async def authenticate_user(self, user_data: UserAuth):
        user = await self.get_user_role(EmailModel(email=user_data.email))
        if user is None or self.validate_password(user_data.password, user.password):
            raise InvalidLoginException(f"Неверный логин или пароль.")
        return user


user_service = UserService(repository_factory=user_repository_factory)
