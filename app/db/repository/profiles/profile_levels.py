from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from db.models import (
    ProfileLevel,
    LevelSkill,
    Skill,
    Stage,
)
from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler


class LevelRepository(BaseRepository):
    model = ProfileLevel

    @db_exception_handler
    async def get_last_level_by_num(self, profile_id: int, level_num: int):

        stmt = select(ProfileLevel).where(
            ProfileLevel.profile_id == profile_id,
            ProfileLevel.is_active.is_(True),
            ProfileLevel.num == level_num,
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_skills_cnt(self, profile_level_id):
        stmt = select(func.count(LevelSkill.id)).where(
            LevelSkill.profile_level_id == profile_level_id
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_level_structure(self, profile_level_id: int):
        stmt = (
            select(ProfileLevel)
            .where(ProfileLevel.id == profile_level_id)
            .options(
                selectinload(ProfileLevel.skills)
                .load_only(Skill.id, Skill.title)
                .selectinload(Skill.stages)
                .load_only(Stage.id, Stage.confirmation_type)
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_profile_count_by_skill(self, skill_id):
        stmt = (
            select(func.count(func.distinct(ProfileLevel.profile_id)))
            .select_from(ProfileLevel)
            .join(
                LevelSkill,
                LevelSkill.profile_level_id == ProfileLevel.id,
            )
            .where(LevelSkill.skill_id == skill_id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

class LevelSkillRepository(BaseRepository):
    model = LevelSkill

    @db_exception_handler
    async def delete_by_skill_ids(self, level_id: int, skills: list[int]):
        stmt = delete(LevelSkill).where(
            LevelSkill.profile_level_id == level_id, LevelSkill.skill_id.in_(skills)
        )
        return await self._session.execute(stmt)
