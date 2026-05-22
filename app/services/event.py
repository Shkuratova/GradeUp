from sqlalchemy.ext.asyncio import AsyncSession

from schemas.event import (
    RegistrationEvent,
    RegistrationPayload,
    EventFilter,
    SetProfilePayload,
    SetProfileEvent,
)
from schemas.profiles import ProfileBase
from schemas.user_profile import UserProfileBase, UserStageBase
from schemas.users import UserInfo, SUser
from services.base import BaseService
from db.repository import (
    EventRepository,
    UserRepository,
    UserProfileRepository,
    ProfileRepository,
)
from db.models.events import EventType, TargetType
from utils.roles import UserRole


class EventService(BaseService):
    entity_name = "Событие"

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = EventRepository(session)
        self.user_repository = UserRepository(session)
        self.profile_repository = ProfileRepository(session)
        self.user_profile_repository = UserProfileRepository(session)

    async def get_events(self, filters: EventFilter):
        filter_dict = filters.model_dump(exclude_none=True)
        return await self.repository.get_events(filter_dict)

    async def registration_log(self, user: UserInfo, current_user: UserInfo):
        event = RegistrationPayload(
            user_id=user.id, email=user.email, department_id=user.department_id
        )
        username = user.get_name_with_email()
        event = RegistrationEvent(
            actor_id=current_user.id,
            actor_role=current_user.role_name,
            target_id=user.id,
            target_type=TargetType.USER,
            event_type=EventType.REGISTRATION,
            message=f"Зарегистрирован пользователь {username}.",
            payload=event.model_dump(),
        )
        await self.repository.add(event.model_dump())

    async def set_user_profile(
        self, user_profile: UserProfileBase, current_user: UserInfo
    ):
        profile_payload = SetProfilePayload(
            profile_id=user_profile.profile_id,
            department_id=current_user.department_id
        )
        user: UserInfo = await self.user_repository.get_user_role({'id':user_profile.user_id})
        profile: ProfileBase = await self.profile_repository.get_by_id(user_profile.profile_id)
        event = SetProfileEvent(
            actor_id=current_user.id,
            actor_role=UserRole.SUPERVISOR,
            target_id=user_profile.id,
            target_type=TargetType.USER_PROFILE,
            event_type=EventType.SET_PROFILE,
            message=f"Сотруднику {user.get_name_with_email()} назначен профиль {profile.title.__repr__()}.",
            payload=profile.model_dump(),
        )
        await self.repository.add(event.model_dump())

    async def schedule_log(self, current_user: UserInfo):
        pass

    async def gradeup_log(self, current_user: UserInfo):
        pass

    async def evaluate_stage_log(self, user_stage: UserStageBase, current_user: UserInfo):
        pass
