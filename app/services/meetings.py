import logging
logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession

from db.models.types import CertificationRole, CertificationStatus
from db.repository import (
    MeetingRepository,
    ParticipantsRepository,
    StageRepository,
    UserStageRepository,
    UserSkillRepository,
    UserLevelRepository,
    StageVersionRepository, UserProfileRepository,
)
from exceptions.common import (
    NotFoundException,
    DataValidationError,
    AlreadyExistException,
)
from exceptions.user import ForbiddenException
from schemas.meetings import (
    MeetingAddForm,
    MeetingFilters,
    MeetingUpdateForm,
    MeetingDetail,
    MeetingAddResult,
)
from schemas.users import UserInfo, UserBase
from services import AccessService
from services.base import BaseService
from services.department import DepartmentService
from services.user import UserService
from services.user_stage import UserStageService
from utils.roles import UserRole


class MeetingService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = MeetingRepository(session)
        self.participant_repository = ParticipantsRepository(session)
        self.stage_version_repository = StageVersionRepository(session)
        self.user_stage_service = UserStageService(session)
        self.user_service = UserService(session)
        self.user_profile_repository = UserProfileRepository(session)

    async def get_meeting_by_id(self, meeting_id: int):
        meeting = await self.repository.get_meeting({'id':meeting_id})
        if meeting is None:
            raise NotFoundException(f"Встреча с id={meeting_id} не найдена.")
        return MeetingDetail.model_validate(meeting, from_attributes=True)

    async def get_meeting_by_filters(self, filters: MeetingFilters):
        filter_dict = filters.model_dump(exclude_none=True)
        meeting = await self.repository.get_meeting(filter_dict)
        if meeting is None:
            raise NotFoundException(f"Встреча с параметрами {filter_dict} не найдена.")
        return MeetingDetail.model_validate(meeting, from_attributes=True)

    async def get_meetings(self, filters: MeetingFilters):
        filter_dict = filters.model_dump(exclude_none=True)
        return await self.repository.get_meeting_list(filter_dict)

    async def get_user_next_meeting(self, user_id: int):
        res = await self.repository.get_next_meeting(user_id)
        if res is None:
            return {"detail": "У пользователя нет запланированных встреч"}
        return MeetingDetail.model_validate(res, from_attributes=True)

    async def get_meeting_student_id(self, meeting_id: int):
        student_id =  await self.participant_repository.get_student(meeting_id)
        if student_id is None:
            raise NotFoundException(f'Не найдена встреча для аттестуемого с meeting_id={meeting_id}')
        return student_id

    async def _validate_participants(
        self, student_id: int, examiner_id: int, current_user: UserInfo
    ):
        user_service = UserService(self.session)
        student = await user_service.get_user_role(UserBase(id=student_id))
        examiner = await user_service.get_user_role(UserBase(id=examiner_id))
        department_ids = await AccessService(
            self.session
        ).get_managed_departments(current_user)
        logging.info('Доступных отделов: %s', len(department_ids) )
        if department_ids is not None and current_user.role_name != UserRole.ADMIN:
            if student.department_id not in department_ids or (
                examiner.department_id not in department_ids
                and examiner.id != current_user.id
            ):
                raise ForbiddenException(
                    "Руководитель может выбирать Аттестуемого и Аттестующего только из своих подчиненных."
                )
        return student

    async def schedule_meeting(self, meeting: MeetingAddForm, current_user: UserInfo):
        filters = MeetingFilters(
            stage_id=meeting.stage_id,
            user_id=meeting.student_id,
            user_role=CertificationRole.student,
            status=CertificationStatus.planned,
            start_date=meeting.started_at
        )
        meetings = await self.repository.get_meeting(filters.model_dump(exclude_none=True))
        if meetings is not None:
            raise AlreadyExistException(
                f"Встреча с заданными параметрами уже назначена на {meetings.started_at}."
            )
        student = await self._validate_participants(
            meeting.student_id, meeting.examiner_id, current_user
        )
        user_stage = await self.user_stage_service.ensure_user_stage(student.id, meeting.stage_id)

        new_meeting = {
            "user_stage_id": user_stage.id,
            "created_by": current_user.id,
            **meeting.model_dump(exclude={"student_id", "examiner_id", "stage_id"}),
        }
        new_meeting = await self.repository.add(new_meeting)

        participants = [
            {
                "meeting_id": new_meeting.id,
                "user_id": meeting.student_id,
                "role": CertificationRole.student,
            },
            {
                "meeting_id": new_meeting.id,
                "user_id": meeting.examiner_id,
                "role": CertificationRole.examiner,
            },
        ]
        await self.participant_repository.add_list(participants)

        return await self.get_meeting_by_id(new_meeting.id)

    async def update_meeting(
        self, meeting_id: int, meeting: MeetingUpdateForm, current_user: UserInfo
    ):
        meeting_filters = MeetingFilters(id=meeting_id)
        old_meeting = await self.get_meetings(meeting_filters)
        if old_meeting is None:
            raise NotFoundException(f"Встреча с id = {meeting.id} не найдена.")
        if meeting.student_id and meeting.examiner_id:
            await self._validate_participants(
                meeting.student_id, meeting.examiner_id, current_user
            )

        upd_meeting = meeting.model_dump(
            exclude={"id", "student_id", "examiner_id", "stage_id"}
        )

        examiner_changed = (
            old_meeting.examiner.user_id != meeting.examiner_id and meeting.examiner_id
        )
        stage_changed = old_meeting.stage_id != meeting.stage_id

        if examiner_changed:
            await self.participant_repository.update_by_id(
                old_meeting.examiner.id, {"user_id": meeting.examiner_id}
            )
        if  stage_changed:
            user_stage = await self.user_stage_service.ensure_user_stage(meeting.student_id, meeting.stage_id)
            upd_meeting["user_stage_id"] = user_stage.id

        await self.repository.update_by_id(meeting_id, upd_meeting)
        return await self.get_meetings(meeting_filters)

    async def get_participant_role(self, meeting_id: int, user_id: int):
        res = await self.participant_repository.get_participant_role(
            meeting_id, user_id
        )
        if res is None:
            raise NotFoundException(
                f"Участник с user_id = {user_id} не назначени на встречу с meeting_id = {meeting_id}."
            )
        return res

    async def _check_supervisor_access(
        self, meeting: MeetingDetail, current_user: UserInfo
    ):
        if meeting.student.user_id == current_user.id:
            return

        student = await self.user_service.get_by_id(meeting.student.id)

        department_ids = await AccessService(
            self.session
        ).get_managed_departments(current_user)

        if student.department_id not in department_ids:
            raise ForbiddenException("Отказано в доступе.")

    async def _check_examiner_access(self, meeting_id: int, user_id: int):
        participant_role = await self.get_participant_role(meeting_id, user_id)
        if participant_role != CertificationRole.examiner:
            raise ForbiddenException("Отказано в доступе.")

    async def get_questions(self, meeting_id: int, current_user: UserInfo):
        meeting: MeetingDetail = await self.get_meeting_by_filters(
            MeetingFilters(id=meeting_id)
        )

        if current_user.is_supervisor:
            await self._check_supervisor_access(meeting, current_user)

        elif current_user.role_name == UserRole.EMPLOYEE:
            await self._check_examiner_access(meeting_id, current_user.id)

        return await self.stage_version_repository.get_questions(
            meeting.stage_version_id
        )
