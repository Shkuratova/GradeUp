from pydantic import BaseModel

from schemas.users import UserAdd, UserInfo
from db.uow import unit_of_work
from db.repository.user import user_repository_factory, UserRepository
import bcrypt
from schemas.users import UserAuth, UserRole, EmailModel, SUser
from exceptions.user import InvalidLoginException
from exceptions.common import NotFoundException, AlreadyExistException
from services.base import BaseService


class UserService(BaseService):
    entity_name = "Пользователь"
    unique_field = "email"

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def validate_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )



    # async def get_by_id(self, user_id: int) -> SUser:
    #     async with unit_of_work() as uow:
    #         repository = self.repository_factory(uow.session)
    #         user = await repository.get_by_id(user_id)
    #         if user is None:
    #             raise UserNotFoundException("Пользователь не найден")
    #         return SUser.model_validate(user)

    async def get_user_role(self, filters: BaseModel) -> UserInfo:
        filter_dict = filters.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            user_repository: UserRepository = self.repository_factory(uow.session)
            user = await user_repository.get_user_role(filter_dict)
            if user is None:
                raise NotFoundException("Пользователь не найден")
            return user

    async def authenticate_user(self, user_data: UserAuth):
        user = await self.get_user_role(EmailModel(email=user_data.email))
        if user is None or self.validate_password(user_data.password, user.password):
            raise InvalidLoginException(f"Неверный логин или пароль.")
        return user


user_service = UserService(repository_factory=user_repository_factory)
