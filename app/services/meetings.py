from sqlalchemy.ext.asyncio import AsyncSession

from db.models.types import CertificationRole
from db.repository import MeetingRepository, ParticipantsRepository, StageRepository
from exceptions.common import NotFoundException
from schemas.meetings import (
    MeetingAddForm,
    MeetingFilters,
    MeetingAdd,
    MeetingUpdateForm,
    MeetingDetail,
)
from schemas.users import UserInfo
from services.base import BaseService
from utils.roles import UserRole

class MeetingService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = MeetingRepository(session)
        self.participant_repository = ParticipantsRepository(session)
        self.stage_repository = StageRepository(session)

    async def get_meetings(self, filters: MeetingFilters):
        filter_dict = filters.model_dump(exclude_none=True)
        return await self.repository.get_meetings(filter_dict)

    async def get_user_next_meeting(self, user_id: int):
        res = await self.repository.get_next_meeting(user_id)
        if res is None:
            return {"detail": "У пользователя нет запланированных встреч"}
        return MeetingDetail.model_validate(res, from_attributes=True)

    async def schedule_meeting(self, meeting: MeetingAddForm, current_user_id: int):

        stage_version = await self.stage_repository.get_last_version_by_id(meeting.stage_id)

        if stage_version is None:
            raise NotFoundException(f"Этап подтверждения с id = {meeting.stage_id} не найден.")

        new_meeting = {
            "stage_version_id": stage_version.id,
            "created_by": current_user_id,
            **meeting.model_dump(exclude={"student_id", "examiner_id", "stage_id"})
        }
        new_meeting = await self.repository.add(new_meeting)


        participants = [
            {
                'meeting_id': new_meeting.id,
                'user_id': meeting.student_id,
                'role':CertificationRole.student
            },
            {
                'meeting_id': new_meeting.id,
                'user_id': meeting.examiner_id,
                'role':CertificationRole.examiner
            }
        ]
        res = await self.participant_repository.add_list(participants)
        return new_meeting

    async def update_meeting(self, meeting: MeetingUpdateForm):
        pass
