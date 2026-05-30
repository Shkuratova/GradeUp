import logging

logger = logging.getLogger(__name__)

from sqlalchemy.ext.asyncio import AsyncSession

from db.models.types import CertificationRole, CertificationStatus
from db.repository import (
    MeetingRepository,
    ParticipantsRepository,
    StageVersionRepository,
    UserProfileRepository,
    SkillRepository,
)
from exceptions.common import (
    NotFoundException,
    AlreadyExistException,
    ConflictException,
)
from exceptions.user import ForbiddenException
from schemas.meetings import (
    MeetingAddForm,
    MeetingFilters,
    MeetingUpdateForm,
    MeetingDetail,
    MeetingQuestions,
)
from schemas.users import UserInfo
from services import AccessService
from services.base import BaseService
from services.users.user import UserService
from services.users.user_stage import UserStageService
from utils.roles import UserRole


class MeetingService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = MeetingRepository(session)
        self.skill_repository = SkillRepository(session)
        self.participant_repository = ParticipantsRepository(session)
        self.stage_version_repository = StageVersionRepository(session)
        self.user_stage_service = UserStageService(session)
        self.user_service = UserService(session)
        self.user_profile_repository = UserProfileRepository(session)

    async def get_meeting_by_id(self, meeting_id: int):
        meeting = await self.repository.get_meeting({"id": meeting_id})
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
        meetings = await self.repository.get_meeting_list(filter_dict)
        return [MeetingDetail.model_validate(m, from_attributes=True) for m in meetings]

    async def get_user_next_meeting(self, user_id: int):
        res = await self.repository.get_next_meeting(user_id)
        if res is None:
            return {"detail": "У пользователя нет запланированных встреч"}
        return MeetingDetail.model_validate(res, from_attributes=True)

    async def get_meeting_student_id(self, meeting_id: int):
        student_id = await self.participant_repository.get_student(meeting_id)
        if student_id is None:
            raise NotFoundException(
                f"Не найдена встреча для аттестуемого с meeting_id={meeting_id}"
            )
        return student_id

    async def _validate_participant(self, employee_id, current_user: UserInfo):
        user_service = UserService(self.session)
        employee = await user_service.get_user_info(employee_id)
        try:
            await AccessService(self.session).can_manage_user(employee_id, current_user)
        except ForbiddenException:
            raise ForbiddenException(
                "Руководитель может выбирать Аттестуемого и Аттестующего только из своих подчиненных."
            )
        return employee

    async def schedule_meeting(self, meeting: MeetingAddForm, current_user: UserInfo):
        if meeting.examiner_id == meeting.student_id:
            raise ConflictException(
                "Невозможно назначить встречу: examiner_id и student_id совпадают."
            )

        filters = MeetingFilters(
            stage_id=meeting.stage_id,
            user_id=meeting.student_id,
            user_role=CertificationRole.student,
            status=CertificationStatus.planned,
            start_date=meeting.started_at,
        )
        meetings = await self.repository.get_meeting(
            filters.model_dump(exclude_none=True)
        )
        if meetings is not None:
            raise AlreadyExistException(
                f"Встреча с заданными параметрами уже назначена на {meetings.started_at}."
            )
        student = await self._validate_participant(meeting.student_id, current_user)
        examiner = await self._validate_participant(meeting.examiner_id, current_user)
        user_stage = await self.user_stage_service.ensure_user_stage(
            student.id, meeting.stage_id
        )

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
        old_meeting = await self.get_meeting_by_id(meeting_id)

        upd_meeting = meeting.model_dump(
            exclude={"id", "student_id", "examiner_id", "stage_id"}
        )

        if old_meeting.examiner.user_id != meeting.examiner_id and meeting.examiner_id:
            if meeting.examiner_id == old_meeting.student.user_id:
                raise ConflictException(
                    "Невозможно назначить встречу: examiner_id и student_id совпадают."
                )

            examiner = await self._validate_participant(
                meeting.examiner_id, current_user
            )
            await self.participant_repository.update_by_id(
                old_meeting.examiner.id, {"user_id": meeting.examiner_id}
            )

        if old_meeting.stage_id != meeting.stage_id:
            user_stage = await self.user_stage_service.ensure_user_stage(
                meeting.student_id, meeting.stage_id
            )
            upd_meeting["user_stage_id"] = user_stage.id

        await self.repository.update_by_id(meeting_id, upd_meeting)

        return await self.get_meeting_by_id(meeting_id)

    async def get_participant_role(self, meeting_id: int, user_id: int):
        res = await self.participant_repository.get_participant_role(
            meeting_id, user_id
        )
        if res is None:
            raise NotFoundException(
                f"Участник с user_id = {user_id} не назначени на встречу с meeting_id = {meeting_id}."
            )
        return res

    async def get_current_user_role(
        self, meeting_id: int, student_id: int, current_user: UserInfo
    ):
        role = CertificationRole.student
        if (
            current_user.is_admin()
            or current_user.is_division_supervisor()
            or (
                current_user.is_department_supervisor()
                and current_user.id != student_id
            )
        ):
            role = CertificationRole.supervisor

        elif current_user.role_name == UserRole.EMPLOYEE:
            participant_role = await self.get_participant_role(
                meeting_id, current_user.id
            )
            if participant_role == CertificationRole.examiner:
                role = CertificationRole.examiner
        return role

    async def get_questions(self, meeting_id: int, current_user: UserInfo):
        meeting: MeetingDetail = await self.get_meeting_by_id(meeting_id)
        role = self.get_current_user_role(meeting_id, meeting.student.id, current_user)

        skill = await self.skill_repository.get_by_id(meeting.skill_id)
        questions = None
        if role != CertificationRole.student:
            stage_version = await self.stage_version_repository.get_questions(
                meeting.stage_version_id
            )
            questions = stage_version.questions

        return MeetingQuestions(
            skill_id=skill.id,
            title=skill.title,
            description=skill.description,
            literature=skill.literature,
            questions=questions,
        )

    async def set_status(
        self, meeting_id: int, status: CertificationStatus, current_user: UserInfo
    ):
        meeting: MeetingDetail = await self.get_by_id(meeting_id)

        if meeting.status == CertificationStatus.completed:
            raise ConflictException("Нельзя изменить статус завершненной встречи.")

        await self.repository.update_by_id(meeting_id, {"status": status})
