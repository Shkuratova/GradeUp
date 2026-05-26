import logging
logger = logging.getLogger(__name__)

import bcrypt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import UserRepository, RoleRepository, DepartmentRepository
from exceptions.common import NotFoundException, ConflictException
from exceptions.user import (
    InvalidLoginException,
    PasswordDontMatchException,
)
from schemas.users import UserAuth, UserFilter, UserUpdateBase
from schemas.users import UserInfo
from services.base import BaseService
from utils.roles import UserRole


class UserService(BaseService):
    entity_name = "Пользователь"
    unique_fields = ["email"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = UserRepository(self.session)
        self.role_repository = RoleRepository(self.session)
        self.department_repository = DepartmentRepository(self.session)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def validate_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    async def add(self, user_model: BaseModel):
        if user_model.password != user_model.confirm_password:
            raise PasswordDontMatchException("Пароли не совпадают.")
        user_model.password = self.hash_password(user_model.password)

        new_user = await super().add(user_model)
        logger.info("Добавлен пользователь %s", user_model.email)
        return new_user

    async def get_users(self, filters: UserFilter):
        filter_dict = filters.model_dump(exclude_none=True)
        return await self.repository.get_all(filter_dict)

    async def get_user_info(
        self, user_id: int | None = None, email: str | None = None
    ) -> UserInfo:
        if user_id is None and email is None:
            raise ValueError("Необходимо передать либо user_id либо email")
        user = await self.repository.get_user_info(user_id, email)
        if user is None:
            raise NotFoundException("Пользователь не найден")
        return UserInfo.model_validate(user)

    async def authenticate_user(self, user_data: UserAuth):
        user = await self.get_user_info(email=str(user_data.email))
        if user is None or not self.validate_password(
            user_data.password, user.password
        ):
            raise InvalidLoginException("Неверный логин или пароль.")
        return UserInfo.model_validate(user)

    async def update(self, user_id: int, user_data: BaseModel, current_user: UserInfo):
        if current_user.role_name != UserRole.ADMIN:
            user_data = UserUpdateBase.model_validate(user_data.model_dump())
        if user_data.role_id is not None:
            role = await self.role_repository.get_by_id(user_data.role_id)
            if role is None:
                raise NotFoundException(f"Роль с id={user_data.role_id} не найдена")

        old = await self.get_user_info(user_id=user_id)
        if (
            old.is_supervisor()
            and old.managed_division is None
            and old.department_id != user_data.department_id
        ):
            raise ConflictException(
                "Нельзя изменить отдел руководителя, пока он назначен руководителем этого отдела."
            )
        if old.managed_division and user_data.department_id:
            raise ConflictException(
                "Руководитель направления не может быть привязан к отделу."
            )

        user_dict = user_data.model_dump(exclude_none=True)
        await self.check_unique_constraint(user_dict, user_id)
        await self.repository.update_by_id(user_id, user_dict)

        return await self.get_user_info(user_id=user_id), old
