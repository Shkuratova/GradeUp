from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from db.models import UserStage, Stage, Skill, StageVersion, UserSkill
from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler

import logging

logger = logging.getLogger(__name__)


class UserStageRepository(BaseRepository):
    model = UserStage

    @db_exception_handler
    async def accepted_count(self, skill_id: int, user_skill_id: int):
        stmt = (
            select(func.count(UserStage.id))
            .join(StageVersion, StageVersion.id == UserStage.stage_version_id)
            .where(
                UserStage.user_skill_id == user_skill_id,
                UserStage.is_accepted.is_(True),
                StageVersion.stage_id.in_(
                    select(Stage.id).where(Stage.skill_id == skill_id)
                ),
            )
        )
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение количества зачтенных этапов навыка (skill_id, user_skill_id)",
            skill_id,
            user_skill_id,
        )
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_evaluation(self, user_stage_id):
        stmt = (
            select(UserStage)
            .where(UserStage.id == user_stage_id)
            .options(
                joinedload(UserStage.skill).load_only(Skill.id, Skill.title),
                joinedload(UserStage.stage).load_only(
                    Stage.id, Stage.confirmation_type
                ),
            )
        )
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение оценки этапа пользователя (user_stage_id=%s)",
            user_stage_id,
        )
        return res.scalar_one_or_none()

    @db_exception_handler
    async def stages_cnt(self, stage_id: int):
        stmt = (
            select(StageVersion.stage_id, func.count(UserStage.stage_version_id))
            .join(StageVersion, StageVersion.id == UserStage.stage_version_id)
            .where(StageVersion.stage_id == stage_id)
            .group_by(StageVersion.stage_id)
        )
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение количетства зачтенных этапов сотрудников по id этапа (stage_id=%s)",
            stage_id,
        )
        return res.scalar_one_or_none()

    async def get_user_id(self, user_stage_id):
        stmt = (
            select(UserSkill.user_id)
            .select_from(UserStage)
            .join(UserSkill, UserSkill.id == UserStage.user_skill_id)
            .where(UserStage.id == user_stage_id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()