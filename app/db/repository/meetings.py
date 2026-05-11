from sqlalchemy import select, exists, and_
from sqlalchemy.orm import joinedload, selectinload

from db.models.skills import StageVersion, Stage, Skill
from db.models.types import CertificationStatus
from db.repository import BaseRepository
from db.models import Meeting, MeetingParticipant, User
from datetime import datetime, timezone


class MeetingRepository(BaseRepository):
    model = Meeting

    async def get_meetings(self, filter_dict: dict):
        stmt = select(Meeting)

        if meeting_id := filter_dict.pop("id", None):
            stmt = stmt.where(Meeting.id == meeting_id)

        if user_id := filter_dict.pop("user_id", None):
            stmt = stmt.where(
                Meeting.participants.any(MeetingParticipant.user_id == user_id)
            )

        if (start_date := filter_dict.pop("start_date", None)) and (
            end_date := filter_dict.pop("end_date", None)
        ):
            stmt = stmt.where(Meeting.started_at.between(start_date, end_date))

        if status := filter_dict.pop("status", None):
            stmt = stmt.where(Meeting.status == status)

        confirmation_type = filter_dict.pop("confirmation_type", None)
        skill_id = filter_dict.pop("skill_id", None)
        if confirmation_type or skill_id:
            stage_exists = exists(
                select(StageVersion)
                .join(StageVersion.stage)
                .where(StageVersion.id == Meeting.stage_version_id)
            )

            if confirmation_type:
                stage_exists = stage_exists.where(
                    Stage.confirmation_type == confirmation_type
                )
            if skill_id:
                stage_exists = stage_exists.where(Stage.skill_id == skill_id)

            stmt = stmt.where(stage_exists)

        if department_id := filter_dict.pop("department_id", None):
            stmt = stmt.where(
                exists(
                    select(MeetingParticipant)
                    .join(MeetingParticipant.user)
                    .where(
                        and_(
                            MeetingParticipant.meeting_id == Meeting.id,
                            User.department_id == department_id,
                        )
                    )
                )
            )

        stmt = stmt.options(
            joinedload(Meeting.stage_version)
            .load_only(StageVersion.id)
            .options(
                joinedload(StageVersion.stage)
                .load_only(Stage.confirmation_type)
                .options(joinedload(Stage.skill).load_only(Skill.title))
            ),
            selectinload(Meeting.participants).options(
                joinedload(MeetingParticipant.user).load_only(
                    User.first_name, User.last_name, User.patronymic, User.department_id
                )
            ),
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()

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
                joinedload(Meeting.stage_version)
                .load_only(StageVersion.id)
                .options(
                    joinedload(StageVersion.stage)
                    .load_only(Stage.confirmation_type)
                    .options(joinedload(Stage.skill).load_only(Skill.title))
                ),
                selectinload(Meeting.participants).options(
                    joinedload(MeetingParticipant.user).load_only(
                        User.first_name,
                        User.last_name,
                        User.patronymic,
                        User.department_id,
                    )
                ),
            )
            .order_by(Meeting.started_at)
            .limit(1)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

class ParticipantsRepository(BaseRepository):
    model = MeetingParticipant
