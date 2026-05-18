import bcrypt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import UserRepository
from exceptions.common import NotFoundException
from exceptions.user import InvalidLoginException
from schemas.users import UserAuth, EmailModel, SUserFilter
from schemas.users import UserInfo
from services.base import BaseService
from services.department import DepartmentService


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
        user_model.password = self.hash_password(user_model.password)

        new_user = await super().add(user_model)
        return new_user

    async def get_users(self, filters: SUserFilter, department_ids: list[int] | None):
        filter_dict = filters.model_dump(exclude_none=True)
        return await self.repository.get_all(filter_dict, department_ids)


    async def get_user_role(self, filters: BaseModel, department_ids: list[int] | None = None) -> UserInfo:
        filter_dict = filters.model_dump(exclude_none=True)
        user = await self.repository.get_user_role(filter_dict, department_ids)
        if user is None:
            raise NotFoundException("Пользователь не найден")
        return UserInfo.model_validate(user)

    async def authenticate_user(self, user_data: UserAuth):
        user = await self.get_user_role(EmailModel(email=user_data.email))
        if user is None or not self.validate_password(
            user_data.password, user.password
        ):
            raise InvalidLoginException(f"Неверный логин или пароль.")
        return UserInfo.model_validate(user)
