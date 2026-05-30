from sqlalchemy.ext.asyncio import AsyncSession

from db.models.types import EventType, TargetType
from db.repository import (
    EventRepository,
    UserRepository,
)
from schemas.departments import (
    DepartmentDetail,
    DivisionDetail,
)
from schemas.evaluations import EvaluationSchema
from schemas.event import (
    RegistrationPayload,
    EventFilter,
    SetProfilePayload,
    EventAdd,
)
from schemas.meetings import MeetingDetail
from schemas.user_profile import UserProfileSchema, GradeUpResult
from schemas.users import UserInfo, RoleSchema
from services.base import BaseService
from utils.roles import UserRole


class EventService(BaseService):
    entity_name = "Событие"

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = EventRepository(session)
        self.user_repository = UserRepository(session)

    async def get_events(self, filters: EventFilter):
        filter_dict = filters.model_dump(exclude_none=True)
        return await self.repository.get_events(filter_dict)

    async def get_employee(self, user_id: int):
        user = await self.user_repository.get_user_info(user_id=user_id)
        return UserInfo.model_validate(user, from_attributes=True)

    async def log_event(
        self,
        *,
        actor_id: int,
        access_scope: UserRole,
        target_id: int,
        target_type: TargetType,
        event_type: EventType,
        message: str,
        payload: dict,
    ):
        event = EventAdd(
            actor_id=actor_id,
            access_scope=access_scope,
            target_id=target_id,
            target_type=target_type,
            event_type=event_type,
            message=message,
            payload=payload,
        )
        await self.repository.add(event.model_dump())

    @staticmethod
    def _division_payload(division: DivisionDetail):
        return {
            "division_id": division.id,
            "division_name": division.division_name,
            "supervisor_id": division.supervisor.id,
            "full_name": division.supervisor.full_name(),
            "supervisor_email": division.supervisor.email,
        }

    @staticmethod
    def _department_payload(department):
        return {
            "department_id": department.id,
            "department_name": department.department_name,
            "supervisor_id": department.supervisor_id,
            "full_name": department.supervisor.full_name(),
            "supervisor_email": department.supervisor.email,
        }

    async def log_registration(self, user: UserInfo, current_user: UserInfo):
        message = f"Зарегистрирован пользователь {user.name_with_email()}."
        payload = RegistrationPayload(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name(),
            department_id=user.department_id,
        )
        await self.log_event(
            actor_id=current_user.id,
            access_scope=current_user.role_name,
            target_id=user.id,
            target_type=TargetType.USER,
            event_type=EventType.REGISTRATION,
            message=message,
            payload=payload.model_dump(),
        )

    async def log_set_user_role(
        self, old_user: UserInfo, user_update: UserInfo, current_user: UserInfo
    ):
        message = (
            f"Изменена роль сотрудника {user_update.name_with_email()} "
            f"с {old_user.role_name} на {user_update.role_name}."
        )
        payload = {
            "user_id": user_update.id,
            "email": user_update.email,
            "department_id": user_update.department_id,
            "full_name": user_update.full_name(),
            "old_role_id": old_user.role_id,
            "old_role": old_user.role_name,
            "new_role_id": user_update.role_id,
            "new_role": user_update.role_name,
        }
        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=user_update.id,
            target_type=TargetType.USER,
            event_type=EventType.ROLE_CHANGED,
            message=message,
            payload=payload,
        )

    async def log_set_user_profile(
        self, user_profile: UserProfileSchema, current_user: UserInfo
    ):
        message = (
            f"Сотруднику {user_profile.user.name_with_email()} "
            f"назначен профиль {user_profile.profile.title.__repr__()}."
        )

        profile_payload = SetProfilePayload(
            user_id=user_profile.user.id,
            email=user_profile.user.email,
            full_name=user_profile.user.full_name(),
            profile_id=user_profile.profile.id,
            title=user_profile.profile.title,
            department_id=user_profile.user.department_id,
        )
        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.SUPERVISOR,
            target_id=user_profile.id,
            target_type=TargetType.USER_PROFILE,
            event_type=EventType.SET_PROFILE,
            message=message,
            payload=profile_payload.model_dump(),
        )

    async def log_gradeup(
        self, user_id: int, gradeup: GradeUpResult, current_user: UserInfo
    ):
        user = await self.get_employee(user_id)
        message = (
            f"Профиль пользователя {user.name_with_email()} "
            f"повышен с уровня {gradeup.old_level.level_name.__repr__()} "
            f"до уровня {gradeup.new_level.level_name.__repr__()}."
        )

        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.SUPERVISOR,
            target_id=user_id,
            target_type=TargetType.USER,
            event_type=EventType.GRADEUP,
            message=message,
            payload={
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name(),
                "department_id": user.department_id,
                **gradeup.model_dump(),
            },
        )

    async def log_schedule(self, meeting: MeetingDetail, current_user: UserInfo):
        message = (
            f"Сотруднику {meeting.student.user.name_with_email()} назначена встреча "
            f"по этапу навыка {meeting.title.__repr__()} ({meeting.confirmation_type}), "
            f"на {meeting.started_at.strftime("%Y-%m-%d %H:%M:%S")}, "
            f"Аттестующий - {meeting.examiner.user.name_with_email()})"
        )
        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.SUPERVISOR,
            target_id=meeting.id,
            target_type=TargetType.MEETING,
            event_type=EventType.SCHEDULE_MEETING,
            message=message,
            payload=meeting.model_dump(),
        )

    async def log_meeting_changed(self, upd, current_user):
        pass

    async def log_evaluate_stage(
        self, user_id: int, user_stage: EvaluationSchema, current_user: UserInfo
    ):
        employee = await self.get_employee(user_id)
        message = (f"Оценен этап пользователя {employee.name_with_email()} "
                   f"{user_stage.skill.title} ({user_stage.confirmation_type}) c оценкой"
                   f" {user_stage.evaluation()}")

        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.SUPERVISOR,
            target_id=user_stage.id,
            target_type=TargetType.USER_STAGE,
            event_type=EventType.EVALUATE,
            message=message,
            payload=user_stage.model_dump()
        )

    async def log_set_division_supervisor(
        self, division: DivisionDetail, current_user: UserInfo
    ):
        message = (
            f"Назначен руководитель направления {division.division_name.__repr__()}: "
            f"{division.supervisor.name_with_email()}"
        )
        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=division.id,
            target_type=TargetType.DIVISION,
            event_type=EventType.SET_DIVISION_SUPERVISOR,
            message=message,
            payload=self._division_payload(division),
        )

    async def log_set_department_supervisor(
        self, department: DepartmentDetail, current_user: UserInfo
    ):
        message = (
            f"Назначен руководитель отдела {department.department_name.__repr__()}: "
            f"{department.supervisor.name_with_email()}"
        )
        event = EventAdd(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=department.id,
            target_type=TargetType.DEPARTMENT,
            event_type=EventType.SET_DEPARTMENT_SUPERVISOR,
            message=message,
            payload=self._department_payload(department),
        )
        await self.repository.add(event.model_dump())

    async def log_remove_division_supervisor(
        self, division: DivisionDetail, current_user
    ):
        message = f"Руководитель направления {division.division_name.__repr__()} был откреплён."
        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=division.id,
            target_type=TargetType.DIVISION,
            event_type=EventType.REMOVE_DIVISION_SUPERVISOR,
            message=message,
            payload=self._division_payload(division),
        )

    async def log_department_supervisor_removed(
        self, department: DepartmentDetail, current_user: UserInfo
    ):
        message = f"Руководитель отдела {department.department_name.__repr__()} был откреплён."
        event = EventAdd(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=department.id,
            target_type=TargetType.DEPARTMENT,
            event_type=EventType.REMOVE_DEPARTMENT_SUPERVISOR,
            message=message,
            payload=self._department_payload(department),
        )
        await self.repository.add(event.model_dump())
