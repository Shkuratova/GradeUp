from sqlalchemy import select, and_, func, not_, exists

from db.models import (
    Skill,
    Stage,
    ProfileLevel,
    StageQuestion,
    StageVersion,
    LevelSkill,
    UserSkill,
    UserStage,
)
from db.repository import BaseRepository
from db.repository.decorators import db_exception_handler


class UserSkillRepository(BaseRepository):
    model = UserSkill

    @db_exception_handler
    async def get_by_user(self, user_id: int, skill_id: int):
        stmt = select(UserSkill).where(
            and_(
                UserSkill.skill_id == skill_id,
                UserSkill.user_id == user_id,
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_skill_detail(self, user_id: int, skill_id: int):
        stmt = (
            select(
                Skill.id.label("skill_id"),
                Skill.title,
                Skill.description,
                Skill.literature,
                Stage.id.label("stage_id"),
                Stage.confirmation_type,
                UserStage.id.label("user_stage_id"),
                UserStage.is_accepted,
                UserStage.comment,
                UserStage.updated_at,
            )
            .select_from(Skill)
            .join(Stage, Stage.skill_id == Skill.id)
            .join(StageVersion, StageVersion.stage_id == Stage.id)
            .outerjoin(
                UserSkill,
                and_(UserSkill.skill_id == Skill.id, UserSkill.user_id == user_id),
            )
            .outerjoin(
                UserStage,
                and_(
                    UserStage.user_skill_id == UserSkill.id,
                    UserStage.stage_version_id == StageVersion.id,
                ),
            )
            .where(Skill.id == skill_id)
        )
        res = await self._session.execute(stmt)
        return res.mappings().all()

    @db_exception_handler
    async def get_skill_detail_questions(self, user_id: int, skill_id: int):
        stmt = (
            select(
                Skill.id.label("skill_id"),
                Skill.title,
                Skill.description,
                Skill.literature,
                Stage.id.label("stage_id"),
                Stage.confirmation_type,
                UserStage.id.label("user_stage_id"),
                UserStage.is_accepted,
                UserStage.comment,
                UserStage.updated_at,
                StageQuestion.num,
                StageQuestion.question,
                StageQuestion.answer,
            )
            .select_from(Skill)
            .join(Stage, Stage.skill_id == Skill.id)
            .join(StageVersion, StageVersion.stage_id == Stage.id)
            .join(StageQuestion, StageQuestion.stage_version_id == StageVersion.id)
            .outerjoin(
                UserSkill,
                and_(
                    UserSkill.skill_id == Skill.id,
                    UserSkill.user_id == user_id,
                ),
            )
            .outerjoin(
                UserStage,
                and_(
                    UserStage.user_skill_id == UserSkill.id,
                    UserStage.stage_version_id == StageVersion.id,
                ),
            )
            .where(Skill.id == skill_id)
        )
        res = await self._session.execute(stmt)
        return res.mappings().all()

    @db_exception_handler
    async def get_accepted_count(self, user_id: int, profile_level_id: int) -> int:
        stmt = select(func.count(UserSkill.id)).where(
            UserSkill.user_id == user_id,
            UserSkill.profile_level_id == profile_level_id,
            UserSkill.is_accepted.is_(True),
        )

        res = await self._session.execute(stmt)

        return res.scalar_one()

    @db_exception_handler
    async def get_count_by_skill(self, skill_id):
        stmt = select(func.count(UserSkill.user_id)).where(
            UserSkill.skill_id == skill_id
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
