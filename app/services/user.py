from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import UserAdd, UserInfo
from db.uow import unit_of_work
from db.repository import UserRepository
from services.department import DepartmentService
from services.profile import ProfileService
import bcrypt
from schemas.users import UserAuth, UserRole, EmailModel, SUser, UserRegistration
from exceptions.user import InvalidLoginException
from exceptions.common import NotFoundException, AlreadyExistException
from services.base import BaseService


class UserService(BaseService):
    entity_name = "Пользователь"
    unique_fields = ["email"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = UserRepository(self.session)


    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def validate_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    async def add(self, user_model: BaseModel):
        if user_model.department_id is not None:
            await DepartmentService(self.session).get_by_id(user_model.department_id)
        if user_model.profile_id is not None:
            await ProfileService(self.session).get_by_id(user_model.profile_id)
        user_model.password = self.hash_password(user_model.password)

        await super().add(user_model)

    # async def get_by_id(self, user_id: int) -> SUser:
    #     async with unit_of_work() as uow:
    #         repository = self.repository_factory(uow.session)
    #         user = await repository.get_by_id(user_id)
    #         if user is None:
    #             raise UserNotFoundException("Пользователь не найден")
    #         return SUser.model_validate(user)

    async def get_user_role(self, filters: BaseModel) -> UserInfo:
        filter_dict = filters.model_dump(exclude_none=True)
        user = await self.repository.get_user_role(filter_dict)
        if user is None:
            raise NotFoundException("Пользователь не найден")
        return UserInfo.model_validate(user)

    async def authenticate_user(self, user_data: UserAuth):
        user = await self.get_user_role(EmailModel(email=user_data.email))
        if user is None or not self.validate_password(user_data.password, user.password):
            raise InvalidLoginException(f"Неверный логин или пароль.")
        return UserInfo.model_validate(user)


