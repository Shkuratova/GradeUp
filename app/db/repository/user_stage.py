from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload

from db.models import UserStage, Stage, Skill
from db.models.user_profiles import UserSkill, UserLevel
from db.repository.base import BaseRepository
from schemas.skills import StageVersion


class UserStageRepository(BaseRepository):
    model = UserStage

    async def get_by_version_id(self, user_id: int, stage_version_id: int):
        stmt = (
            select(UserStage)
            .join(UserStage.user_skill)
            .where(
                UserSkill.user_id == user_id,
                UserStage.stage_version_id == stage_version_id,
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_stage_id(self, stage_id: int):
        stmt = (
            select(UserStage)
            .join(UserStage.stage_version)
            .join(StageVersion.stage)
            .where(Stage.id == stage_id)
        )

        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

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
        return res.scalar_one_or_none()

    async def get_evaluation(self, user_stage_id):
        stmt = (
            select(UserStage)
            .where(UserStage.id == user_stage_id)
            .options(joinedload(UserStage.skill).load_only(Skill.id, Skill.title),
                     joinedload(UserStage.stage).load_only(Stage.id, Stage.confirmation_type))

        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
