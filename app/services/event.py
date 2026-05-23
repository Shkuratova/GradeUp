
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.events import EventType, TargetType
from db.repository import (
    EventRepository,
    UserRepository,
)
from schemas.departments import (
    DepartmentDetail,
    DivisionDetail,
)
from schemas.event import (
    RegistrationPayload,
    EventFilter,
    SetProfilePayload,
    EventAdd,
)
from schemas.user_profile import UserStageBase, UserProfileSchema
from schemas.users import UserInfo
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
        user = await self.user_repository.get_user_role({'id': user_id})
        return UserInfo.model_validate(user, from_attributes=True)

    async def log_event(
        self,
        *,
        actor_id: int,
        access_scope: UserRole,
        target_id: int,
        target_type: TargetType,
        event_type: EventType,
        payload: dict,
    ):
        event = EventAdd(
            actor_id=actor_id,
            access_scope=access_scope,
            target_id=target_id,
            target_type=target_type,
            event_type=event_type,
            payload=payload,
        )
        await self.repository.add(event.model_dump())

    @staticmethod
    def _division_payload(division):
        return {
            "division_id": division.id,
            "division_name": division.division_name,
            "supervisor_id": division.supervisor_id,
            "supervisor_name": division.supervisor.full_name(),
            "supervisor_email": division.supervisor.email
        }
    @staticmethod
    def _department_payload(department):
        return {
            "department_id": department.id,
            "department_name": department.department_name,
            "supervisor_id": department.supervisor_id,
            "supervisor_name": department.supervisor.full_name(),
            "supervisor_email": department.supervisor.email,
        }

    async def log_registration(self, user: UserInfo, current_user: UserInfo):
        payload = RegistrationPayload(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name(),
            department_id=user.department.id,
        )
        await self.log_event(
            actor_id=current_user.id,
            access_scope=current_user.role.role_name,
            target_id=user.id,
            target_type=TargetType.USER,
            event_type=EventType.REGISTRATION,
            payload=payload.model_dump()
        )

    async def log_set_user_profile(
        self, user_profile: UserProfileSchema, current_user: UserInfo
    ):
        profile_payload = SetProfilePayload(
            user_id=user_profile.user_id,
            email=user_profile.user.email,
            full_name=user_profile.user.full_name(),
            profile_id=user_profile.profile_id,
            title=user_profile.profile.title,
            department_id=user_profile.user.department_id,
        )
        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.SUPERVISOR,
            target_id=user_profile.id,
            target_type=TargetType.USER_PROFILE,
            event_type=EventType.SET_PROFILE,
            payload=profile_payload.model_dump(),
        )

    async def log_gradeup(self, user_id: int, profile_id: int, current_user: UserInfo):
        pass

    async def log_schedule(self, meeting, current_user: UserInfo):
        pass


    async def log_meeting_changed(self, upd, current_user):
        pass

    async def log_evaluate_stage(
        self, user_stage: UserStageBase, current_user: UserInfo
    ):
        pass

    async def log_set_division_supervisor(
        self, division: DivisionDetail, current_user: UserInfo
    ):
        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=division.id,
            target_type=TargetType.DIVISION,
            event_type=EventType.SET_DIVISION_SUPERVISOR,
            payload=self._division_payload(division),
        )

    async def log_set_department_supervisor(
        self, department:DepartmentDetail, current_user: UserInfo
    ):
        event = EventAdd(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=department.id,
            target_type=TargetType.DEPARTMENT,
            event_type=EventType.SET_DEPARTMENT_SUPERVISOR,
            payload=self._department_payload(department)
        )
        await self.repository.add(event.model_dump())

    async def log_remove_division_supervisor(
        self, division: DivisionDetail, current_user
    ):
        await self.log_event(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=division.id,
            target_type=TargetType.DIVISION,
            event_type=EventType.REMOVE_DIVISION_SUPERVISOR,
            payload=self._division_payload(division),
        )

    async def log_department_supervisor_removed(
        self, department: DepartmentDetail, current_user: UserInfo
    ):
        event = EventAdd(
            actor_id=current_user.id,
            access_scope=UserRole.ADMIN,
            target_id=department.id,
            target_type=TargetType.DEPARTMENT,
            event_type=EventType.REMOVE_DEPARTMENT_SUPERVISOR,
            payload=self._department_payload(department),
        )
        await self.repository.add(event.model_dump())
