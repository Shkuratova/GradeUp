from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    DepartmentRepository,
    ProfileRepository,
    UserProfileRepository,
    UserRepository,
    SkillRepository,
    ParticipantsRepository,
    UserStageRepository,
)
from db.repository.organization import DepartmentUserRepository
from exceptions.common import NotFoundException
from exceptions.user import ForbiddenException
from schemas.meetings import MeetingFilters
from schemas.users import UserInfo
from services.base import BaseService
from utils.roles import UserRole, CertificationRole
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
        self.user_stage_repository = UserStageRepository(session)
        self.department_user_repository = DepartmentUserRepository(session)

    async def get_managed_departments(self, current_user: UserInfo):

        departments = []
        if current_user.is_admin():
            departments = await self.department_repository.get_departments_id()
        elif current_user.is_division_supervisor():
                departments = await self.department_repository.get_departments_id(
                    current_user.managed_division_id
                )
                logger.warning(
                    "Доступные департаменты для пользователя %s: %s",
                    current_user.name_with_email(),
                    departments,
                )
                if not departments:
                    raise ForbiddenException(
                        "Нет доступных отделов в вашем подразделении."
                    )
        elif current_user.is_department_supervisor() :
            departments = [current_user.department_id]
        else:
            raise ForbiddenException(
                    "Руководитель должен быть привязан к отделу или подразделению."
                )
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
        if current_user.is_admin() or current_user.is_spo():
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
        if current_user.is_admin():
            return
        user = await self.user_repository.get_user_info(user_id)
        if user is None:
            raise NotFoundException(f"Пользователь с user_id = {user_id} не найден.")
        departments_id = await self.get_managed_departments(current_user)
        if user.department_id in departments_id:
            raise ForbiddenException("Отказано в доступе.")


    async def can_get_user(self, user_id: int, current_user: UserInfo):
        user = await self.user_repository.get_user_info(user_id)
        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return
        elif current_user.is_department_supervisor()  or current_user.is_division_supervisor():
            departments_id = await self.get_managed_departments(current_user)
            if user.department_id in departments_id:
                return
        elif current_user.role_name == UserRole.EMPLOYEE:
            if current_user.id == user.id:
                return

        raise ForbiddenException("Нет доступа к выбранному пользователю")

    async def can_get_user_profile(self, user_id: int, current_user: UserInfo):
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

        if current_user.is_department_supervisor():
            await self.can_get_user(user_profile.user_id, current_user)
            return user_profile

        raise ForbiddenException("Нет доступа к профилю пользователя")

    async def can_get_profile(self, profile_id: int, current_user: UserInfo):

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return profile_id

        if current_user.is_department_supervisor():
            departments_id = await self.get_managed_departments(current_user)
            exist = await self.profile_repository.profile_exist(
                profile_id, departments_id
            )
            if exist is not None:
                return profile_id
        raise ForbiddenException("Нет доступа к выбранному профилю.")

    async def can_get_user_profile_questions(
        self, user_id: int, current_user: UserInfo
    ):
        if user_id == current_user.id:
            raise ForbiddenException("Откзано в доступе")
        await self.can_get_user(user_id, current_user)

    async def can_get_skill(self, skill_id: int, current_user: UserInfo):

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return skill_id

        if current_user.is_department_supervisor():
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

    async def can_get_meeting_info(self, meeting_id: int, current_user: UserInfo):
        if current_user.is_admin():
            return
        student = await self.participant_repository.get_one_by_filter({'meeting_id': meeting_id, 'role': CertificationRole.STUDENT})
        if student is None:
            raise NotFoundException("Аттестуемый встречи не найден.")
        examiner = await self.participant_repository.get_one_by_filter({'meeting_id': meeting_id, 'role': CertificationRole.EXAMINER})
        if current_user.id == examiner.user_id:
            return
        elif current_user.is_department_supervisor() or current_user.is_division_supervisor():
            await self.can_manage_user(student.user_id, current_user)

        raise ForbiddenException(f"Нет доступа к выбранной встрече.")

    async def can_manage_meeting(self, meeting_id: int, current_user: UserInfo):
        if current_user.is_admin():
            return
        student = await self.participant_repository.get_one_by_filter({'meeting_id': meeting_id, 'role': CertificationRole.STUDENT})
        if student is None:
            raise NotFoundException("Аттестуемый встречи не найден.")
        if current_user.is_department_supervisor() or current_user.is_division_supervisor():
            await self.can_manage_user(student.user_id, current_user)

        raise ForbiddenException(f"Нет доступа к выбранной встрече.")

    async def can_get_meeting(self, meeting_id: int, current_user: UserInfo):
        student_id = await self.participant_repository.get_student(meeting_id)
        try:
            await self.can_get_user(student_id, current_user)
        except ForbiddenException as error:
            raise ForbiddenException(f"Нет доступа к выбранной встрече.")

    @classmethod
    async def can_get_division(cls, division_id, current_user):
        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return
        if (
            current_user.managed_division_id
            and current_user.managed_division_id == division_id
        ):
            return
        raise ForbiddenException("Нет доступа к выбранному направлению")

    @classmethod
    async def get_managed_division(cls, current_user: UserInfo) -> int | None:
        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return None
        if (
            current_user.is_department_supervisor()
            and current_user.managed_division_id is not None
        ):
            return current_user.managed_division_id

        raise ForbiddenException("Нет доступа к направлениям")

    async def can_get_evaluation(self, user_stage_id: int, current_user: UserInfo):
        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return
        user_id = await self.user_stage_repository.get_user_id(user_stage_id)
        if user_id is None:
            raise NotFoundException(f"Оценка этапа с (user_stage_id={user_stage_id}) не найдена")
        await self.can_get_user(user_id, current_user)

    async def get_meeting_filter(self, filters: MeetingFilters, current_user: UserInfo):
        if current_user.role_name == UserRole.EMPLOYEE:
            filters.user_id = current_user.id
        elif current_user.is_department_supervisor():
            filters.departments_id = await self.get_department_filter(current_user, filters.departments_id)
        return filters
