from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import DepartmentRepository, ProfileRepository, UserProfileRepository, UserRepository, \
    SkillRepository
from exceptions.common import NotFoundException
from exceptions.user import ForbiddenException
from schemas.users import UserInfo
from services.base import BaseService
from utils.roles import UserRole


class AccessService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.department_repository = DepartmentRepository(session)
        self.user_repository = UserRepository(session)
        self.profile_repository = ProfileRepository(session)
        self.user_profile_repository = UserProfileRepository(session)
        self.skill_repository = SkillRepository(session)

    async def get_managed_departments(self, current_user: UserInfo):

        if current_user.role_name == UserRole.EMPLOYEE:
            raise ForbiddenException("Отказано в доступе.")

        departments = []
        if current_user.role_name == UserRole.ADMIN:
            departments =  await self.department_repository.get_departments_id()
        elif current_user.division_id is not None:
            departments = await self.department_repository.get_departments_id(current_user.managed_division.id)
            if not departments:
                raise ForbiddenException("Нет доступных отделов в вашем подразделении.")
        elif current_user.department_id is not None:
            departments = [current_user.department_id]
        else:
            raise ForbiddenException("Руководитель должен быть привязан к отделу или подразделению.")
        return departments

    async def can_access_department(self, department_id: int, current_user: UserInfo):
        if current_user.role_name == UserRole.ADMIN:
            return department_id

        departments_id = await self.get_managed_departments(current_user)

        if department_id not in departments_id:
            raise ForbiddenException("Нет доступа к выбранному отделу.")

        return department_id

    async def get_department_filter(self, current_user: UserInfo, departments_id: list[int] | None = None):
        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return departments_id
        else:
            access_departments = await self.get_managed_departments(current_user)
            if departments_id is None:
                return access_departments
            allowed = set(access_departments)
            requested = set(departments_id)
            if not requested.issubset(allowed):
                raise ForbiddenException("Нет доступа к выбранным отделам.")

            return departments_id

    async def can_manage_user(self, user_id, current_user: UserInfo):
        if current_user.role_name == UserRole.ADMIN:
            return True
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(f"Пользователь с user_id = {user_id} не найден.")
        departments_id = await self.get_managed_departments(current_user)
        if user.department_id not in departments_id:
            raise ForbiddenException("Отказано в доступе.")
        return user

    async def can_get_user(self, user, current_user: UserInfo):

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return
        elif current_user.role_name == UserRole.EMPLOYEE:
            if current_user.id == user.id:
                return
        else:
            departments_id = await self.get_managed_departments(current_user)
            if user.department_id in departments_id:
                return

        raise ForbiddenException("Нет доступа к выбранному пользователю")

    async def can_get_user_profile(self, user_profile_id: int, current_user: UserInfo):
        user_profile = await self.user_profile_repository.get_by_id(user_profile_id)
        if user_profile is None:
            raise NotFoundException(f"Профиль пользователя с user_profile_id = {user_profile_id} не найден")

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return user_profile

        if current_user.id == user_profile.user_id:
            return user_profile

        if current_user.role_name == UserRole.SUPERVISOR:
            user = await self.user_repository.get_by_id(user_profile.user_id)
            await self.can_get_user(user, current_user)
            return user_profile

        raise ForbiddenException("Нет доступа к профилю пользователя")

    async def can_get_profile(self, profile_id: int, current_user: UserInfo):

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return profile_id

        if current_user.role_name == UserRole.SUPERVISOR:
            departments_id = await self.get_managed_departments(current_user)
            exist = await self.profile_repository.profile_exist(profile_id, departments_id)
            if exist is not None:
                return profile_id
        raise ForbiddenException("Нет доступа к выбранному профилю.")

    async def can_get_skill(self, skill_id: int, current_user: UserInfo):

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return skill_id

        if current_user.role_name == UserRole.SUPERVISOR:
            departments_id = await self.get_managed_departments(current_user)
            exist = await self.skill_repository.skill_exist(skill_id, departments_id)
            if exist is not None:
                return skill_id
        raise ForbiddenException("Нет доступа к выбранному навыку.")
