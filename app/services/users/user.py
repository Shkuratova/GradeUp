import logging

from db.models.types import DepartmentRole
from db.repository.organization import DepartmentUserRepository

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
from schemas.users import (
    UserAuth,
    UserFilter,
    UserUpdateBase,
    ResetPassword,
    ChangePassword,
    UserRegistration,
    UserAdd,
)
from schemas.users import UserInfo
from services.base import BaseService


class UserService(BaseService):
    entity_name = "Пользователь"
    unique_fields = ["email"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = UserRepository(self.session)
        self.role_repository = RoleRepository(self.session)
        self.department_repository = DepartmentRepository(self.session)
        self.department_user_repository = DepartmentUserRepository(self.session)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def validate_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    async def add(self, user_model: UserRegistration):
        if user_model.password != user_model.confirm_password:
            raise PasswordDontMatchException("Пароли не совпадают.")

        user = UserAdd(
            email=user_model.email,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            patronymic=user_model.patronymic,
            position=user_model.position,
            password=self.hash_password(user_model.password)
        )
        new_user = await super().add(user)
        if user_model.department_id is not None:
            await self.department_user_repository.add(
                {
                    "user_id": new_user.id,
                    "department_id": user_model.department_id,
                    "role": DepartmentRole.EMPLOYEE,
                }
            )

        logger.info("Добавлен пользователь %s", user_model.email)
        return new_user

    async def get_users(self, filters: UserFilter, current_user: UserInfo):

        filter_dict = filters.model_dump(exclude_none=True)
        users = await self.repository.get_all(filter_dict)
        users = [UserInfo.model_validate(u, from_attributes=True) for u in users]
        if current_user.is_division_supervisor():
            supervisor = await self.get_user_info(current_user.id)
            users.append(UserInfo.model_validate(supervisor, from_attributes=True))
        return users

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
        if not current_user.is_admin():
            user_data = UserUpdateBase.model_validate(user_data.model_dump())
        if user_data.role_id is not None:
            role = await self.role_repository.get_by_id(user_data.role_id)
            if role is None:
                raise NotFoundException(f"Роль с id={user_data.role_id} не найдена")

        old = await self.get_user_info(user_id=user_id)
        if (
            old.is_department_supervisor()
            and old.department_id != user_data.department_id
        ):
            raise ConflictException(
                "Нельзя изменить отдел руководителя, пока он назначен руководителем этого отдела."
            )
        if old.is_division_supervisor() and user_data.department_id:
            raise ConflictException(
                "Руководитель направления не может быть привязан к отделу."
            )
        if user_data.department_id is None:
            await self.department_user_repository.delete_by_user_id(user_id)
        elif old.department_id is None and user_data.department_id is not None:
            await self.department_user_repository.add(
                {
                    "user_id": user_id,
                    "department_id": user_data.department_id,
                    "role": DepartmentRole.EMPLOYEE,
                }
            )
        elif user_data.department_id != old.department_id:
            await self.department_user_repository.update_by_user_id(
                user_id, {"department_id": user_data.department_id}
            )
        user_dict = user_data.model_dump(exclude_none=True, exclude={"department_id"})
        await self.check_unique_constraint(user_dict, user_id)
        await self.repository.update_by_id(user_id, user_dict)

        return await self.get_user_info(user_id=user_id), old

    async def reset_password(self, user_id: int, reset_form: ResetPassword):
        if reset_form.confirm_password != reset_form.password:
            raise PasswordDontMatchException("Пароли не совпадают")

        await self.get_by_id(user_id)
        new_pass = self.hash_password(reset_form.password)
        await self.repository.update_by_id(user_id, {"password": new_pass})

    async def change_password(self, user: UserInfo, change_form: ChangePassword):
        if not self.validate_password(change_form.old_password, user.password):
            raise InvalidLoginException("Неверный пароль")
        if change_form.new_password != change_form.confirm_password:
            raise PasswordDontMatchException("Пароли не совпадают")
        await self.repository.update_by_id(
            user.id, {"password": change_form.new_password}
        )
