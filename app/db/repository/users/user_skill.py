from sqlalchemy import select, and_, func
from sqlalchemy.orm import aliased

from db.models import (
    Skill,
    Stage,
    StageVersion,
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
    async def get_skill_progress(self, user_id: int, skill_id: int):
        skill_progress = (
            select(
                UserSkill.user_id,
                UserSkill.skill_id,
                UserSkill.is_accepted.label("skill_accepted"),
                UserStage.id.label("user_stage_id"),
                StageVersion.stage_id,
                UserStage.stage_version_id,
                UserStage.is_accepted.label("stage_accepted"),
                UserStage.comment,
                UserStage.updated_at,
            )
            .join(UserStage, UserStage.user_skill_id == UserSkill.id)
            .join(StageVersion, StageVersion.id == UserStage.stage_version_id)
            .where(UserSkill.skill_id == skill_id, UserSkill.user_id == user_id)
            .cte("skill_progress")
        )
        sp = aliased(skill_progress)
        skill_structure = (
            select(
                Skill.id.label("skill_id"),
                Skill.title,
                Skill.description,
                Skill.literature,
                Stage.id.label("stage_id"),
                Stage.confirmation_type,
            )
            .join(Stage, Stage.skill_id == Skill.id)
            .where(Skill.id == skill_id)
            .cte("skill_structure")
        )
        ss = aliased(skill_structure)
        stmt = select(
            ss.c.skill_id,
            ss.c.title,
            ss.c.description,
            ss.c.literature,
            sp.c.skill_accepted,
            ss.c.stage_id,
            ss.c.confirmation_type,
            sp.c.stage_version_id,
            sp.c.user_stage_id,
            sp.c.stage_accepted,
            sp.c.comment,
            sp.c.updated_at,
        ).outerjoin(
            sp, and_(sp.c.skill_id == ss.c.skill_id, sp.c.stage_id == ss.c.stage_id)
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
