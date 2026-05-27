from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload, selectinload

from db.models import (
    Meeting,
    MeetingParticipant,
    User,
    UserStage,
    StageVersion,
    Stage,
)
from db.models.types import CertificationStatus, CertificationRole
from db.repository import BaseRepository
from db.repository.decorators import db_exception_handler


class MeetingRepository(BaseRepository):
    model = Meeting

    @staticmethod
    def _get_meeting_query(filter_dict: dict):
        stmt = select(Meeting)

        if meeting_id := filter_dict.pop("id", None):
            stmt = stmt.where(Meeting.id == meeting_id)

        user_id = filter_dict.pop("user_id", None)
        user_role = filter_dict.pop("user_role", None)

        if user_id or user_role:
            participant_filters = []
            if user_id:
                participant_filters.append(MeetingParticipant.user_id == user_id)
            if user_role:
                participant_filters.append(MeetingParticipant.role == user_role)
            stmt = stmt.where(Meeting.participants.any(and_(*participant_filters)))

        start_date = filter_dict.pop("start_date", None)
        end_date = filter_dict.pop("end_date", None)

        if start_date and end_date:
            stmt = stmt.where(Meeting.started_at.between(start_date, end_date))
        elif start_date:
            stmt = stmt.where(Meeting.started_at >= start_date)
        elif end_date:
            stmt = stmt.where(Meeting.started_at <= end_date)

        if status := filter_dict.pop("status", None):
            stmt = stmt.where(Meeting.status == status)

        confirmation_type = filter_dict.pop("confirmation_type", None)
        skill_id = filter_dict.pop("skill_id", None)
        stage_id = filter_dict.pop("stage_id", None)

        if confirmation_type or skill_id or stage_id:
            stmt = (
                stmt.join(Meeting.user_stage)
                .join(UserStage.stage)
            )

            if stage_id:
                stmt = stmt.where(Stage.id == stage_id)

            if confirmation_type:
                stmt = stmt.where(Stage.confirmation_type == confirmation_type)

            if skill_id:
                stmt = stmt.where(Stage.skill_id == skill_id)

        if department_ids := filter_dict.pop("departments_id", None):
            stmt = stmt.where(
                Meeting.participants.any(
                    MeetingParticipant.user.has(User.department_id.in_(department_ids))
                )
            )

        stmt = stmt.options(
            joinedload(Meeting.user_stage)
            .load_only(UserStage.id, UserStage.stage_version_id)
            .options(
                joinedload(UserStage.stage).load_only(Stage.id, Stage.confirmation_type),
                joinedload(UserStage.skill)
            ),
            selectinload(Meeting.participants).options(
                joinedload(MeetingParticipant.user)
            ),
        )

        return stmt

    @db_exception_handler
    async def get_meeting_list(self, filter_dict: dict):
        stmt = self._get_meeting_query(filter_dict)
        res = await self._session.execute(stmt)
        return res.scalars().all()

    @db_exception_handler
    async def get_meeting(self, filter_dict: dict):
        stmt = self._get_meeting_query(filter_dict)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_next_meeting(self, user_id):
        stmt = (
            select(Meeting)
            .where(
                and_(
                    Meeting.participants.any(MeetingParticipant.user_id == user_id),
                    Meeting.started_at > datetime.now(),
                    Meeting.status == CertificationStatus.planned,
                )
            )
            .options(
                joinedload(Meeting.user_stage)
                .load_only(UserStage.id, UserStage.stage_version_id)
                .options(
                    joinedload(UserStage.stage),
                    joinedload(UserStage.skill)
                ),
                selectinload(Meeting.participants).options(
                    joinedload(MeetingParticipant.user)
                ),
            )
            .order_by(Meeting.started_at)
            .limit(1)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


class ParticipantsRepository(BaseRepository):
    model = MeetingParticipant

    @db_exception_handler
    async def get_participant_role(self, meeting_id: int, user_id: int):
        stmt = select(MeetingParticipant.role).where(
            and_(
                MeetingParticipant.meeting_id == meeting_id,
                MeetingParticipant.user_id == user_id,
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_student(self, meeting_id):
        stmt = select(MeetingParticipant.user_id).where(
            MeetingParticipant.meeting_id == meeting_id,
            MeetingParticipant.role == CertificationRole.student,
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
