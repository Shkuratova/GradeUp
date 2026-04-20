from sqlalchemy.orm import contains_eager
from sqlalchemy import select, delete
from db.repository.base import BaseRepository
from db.models import Skill, SkillStage, LevelSkill


class SkillRepository(BaseRepository):
    model = Skill

    async def get_stages(self, filter_dict: dict):
        stmt = (
            select(Skill)
            .join(Skill.stages, isouter=True)
            .options(contains_eager(Skill.stages))
            .filter_by(**filter_dict)
        )
        res = await self._session.execute(stmt)
        return res.unique().scalars().all()

    async def check_list(self, skill_ids: list[int]) -> list[int]:
        stmt = select(Skill.id).where(Skill.id.in_(skill_ids))
        res = await self._session.execute(stmt)
        return list(res.scalars().all())


class StageRepository(BaseRepository):
    model = SkillStage


class LevelSkillRepository(BaseRepository):
    model = LevelSkill

    async def delete_by_skill_ids(self, level_id: int, skills: list[int]):
        stmt = delete(LevelSkill).where(
            LevelSkill.profile_level_id == level_id, LevelSkill.skill_id.in_(skills)
        )
        return await self._session.execute(stmt)
