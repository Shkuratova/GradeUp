from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    DepartmentRepository,
    ProfileRepository,
    UserProfileRepository,
    UserRepository,
    SkillRepository,
    ParticipantsRepository,
)
from exceptions.common import NotFoundException
from exceptions.user import ForbiddenException
from schemas.users import UserInfo
from services.base import BaseService
from utils.roles import UserRole
import logging
logger = logging.getLogger(__name__)

class AccessService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.department_repository = DepartmentRepository(session)
        self.user_repository = UserRepository(session)
        self.profile_repository = ProfileRepository(session)
        self.user_profile_repository = UserProfileRepository(session)
        self.skill_repository = SkillRepository(session)
        self.participant_repository = ParticipantsRepository(session)

    async def get_managed_departments(self, current_user: UserInfo):

        departments = []
        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            departments = await self.department_repository.get_departments_id()
        elif current_user.is_supervisor:
            if current_user.managed_division_id is not None:

                departments = await self.department_repository.get_departments_id(
                    current_user.managed_division.id
                )
                if not departments:
                    raise ForbiddenException(
                        "Нет доступных отделов в вашем подразделении."
                    )
            elif current_user.department_id is not None:
                departments = [current_user.department_id]
            else:
                raise ForbiddenException(
                    "Руководитель должен быть привязан к отделу или подразделению."
                )
        else:
            raise ForbiddenException("Отказано в доступе.")
        return departments

    async def can_access_department(self, department_id: int, current_user: UserInfo):
        if current_user.role_name == UserRole.ADMIN:
            return department_id

        departments_id = await self.get_managed_departments(current_user)

        if department_id not in departments_id:
            raise ForbiddenException("Нет доступа к выбранному отделу.")

        return department_id

    async def get_department_filter(
        self, current_user: UserInfo, departments_id: list[int] | None = None
    ):
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

    async def can_get_user_profile(
        self, user_id: int,  current_user: UserInfo
    ):
        user_profile = await self.user_profile_repository.get_one_by_filter(
            {"user_id": user_id}
        )

        if user_profile is None:
            raise NotFoundException(
                f"Профиль сотрудника с user_id = {user_id}  не найден"
            )

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return user_profile

        if current_user.id == user_profile.user_id:
            return user_profile

        if current_user.is_supervisor:
            user = await self.user_repository.get_by_id(user_profile.user_id)
            await self.can_get_user(user, current_user)
            return user_profile

        raise ForbiddenException("Нет доступа к профилю пользователя")

    async def can_get_profile(self, profile_id: int, current_user: UserInfo):

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return profile_id

        if current_user.is_supervisor:
            departments_id = await self.get_managed_departments(current_user)
            exist = await self.profile_repository.profile_exist(
                profile_id, departments_id
            )
            if exist is not None:
                return profile_id
        raise ForbiddenException("Нет доступа к выбранному профилю.")

    async def can_get_user_profile_questions(self, user_id: int, current_user: UserInfo):
        if user_id == current_user.id:
            raise ForbiddenException("Откзано в доступе")
        user = await self.user_repository.get_by_id(user_id)
        await self.can_get_user(user, current_user)

    async def can_get_skill(self, skill_id: int, current_user: UserInfo):

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return skill_id

        if current_user.is_supervisor:
            departments_id = await self.get_managed_departments(current_user)
            exist = await self.skill_repository.skill_exist(skill_id, departments_id)
            if exist is not None:
                return skill_id
        raise ForbiddenException("Нет доступа к выбранному навыку.")

    @staticmethod
    def get_accessible_event_types(
        event_type: str | None, current_user: UserInfo
    ) -> str | None:
        if event_type is None:
            return
        if current_user.role_name == UserRole.ADMIN:
            return event_type
        if event_type != UserRole.ADMIN:
            return event_type

        raise ForbiddenException("Отказано в доступе.")

    async def can_manage_meeting(self, meeting_id: int, current_user: UserInfo):
        student_id = await self.participant_repository.get_student(meeting_id)
        return await self.can_manage_user(student_id, current_user)

    @classmethod
    async def can_get_division(cls, division_id, current_user):
        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return
        if current_user.managed_division_id and current_user.managed_division_id == division_id:
            return
        raise ForbiddenException("Нет доступа к выбранному направлению")

    @classmethod
    async def get_managed_division(cls, current_user: UserInfo) -> int | None:
        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return None
        if current_user.is_supervisor and current_user.managed_division_id is not None:
            return current_user.managed_division_id

        raise ForbiddenException("Нет доступа к направлениям")


