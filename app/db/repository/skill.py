from sqlalchemy.orm import contains_eager
from sqlalchemy import select, delete
from db.repository.base import BaseRepository
from db.models.skills import (
    Skill,
    Category,
    SkillCategory,
    Stage,
    LevelSkill,
    StageVersion,
    StageQuestion,
)
from db.repository.decorators import db_exception_handler


class SkillRepository(BaseRepository):
    model = Skill

    @db_exception_handler
    async def get_all_by_categories(self, categories: list[int]):
        stmt = (
            select(Skill)
            .join(Skill.categories)
            .where(Category.id.in_(categories))
            .options(contains_eager(Skill.categories).load_only(Category.id))
        )
        res = await self._session.execute(stmt)
        return res.unique().scalars().all()

    @db_exception_handler
    async def get_stages(self, filter_dict: dict):
        stmt = (
            select(Skill)
            .join(Skill.stages, isouter=True)
            .options(contains_eager(Skill.stages))
            .filter_by(**filter_dict)
        )
        res = await self._session.execute(stmt)
        return res.unique().scalars().all()

    @db_exception_handler
    async def check_list(self, skill_ids: list[int]) -> list[int]:
        stmt = select(Skill.id).where(Skill.id.in_(skill_ids))
        res = await self._session.execute(stmt)
        return list(res.scalars().all())


class LevelSkillRepository(BaseRepository):
    model = LevelSkill

    @db_exception_handler
    async def delete_by_skill_ids(self, level_id: int, skills: list[int]):
        stmt = delete(LevelSkill).where(
            LevelSkill.profile_level_id == level_id, LevelSkill.skill_id.in_(skills)
        )
        return await self._session.execute(stmt)


class QuestionRepository(BaseRepository):
    model = StageQuestion

    @db_exception_handler
    async def get_all(self, filter_dict: dict):
        stmt = (
            select(StageQuestion)
            .options(contains_eager(StageQuestion.stage))
            .filter_by(**filter_dict)
        )
        res = await self._session.execute(stmt)
        return res.unique().scalars().all()

    @db_exception_handler
    async def get_questions_id(self, stage_id: int):
        stmt = select(self.model.id).where(self.model.stage_id == stage_id)
        res = await self._session.execute(stmt)
        return res.scalars().all()


class CategoryRepository(BaseRepository):
    model = Category


class SkillCategoryRepository(BaseRepository):
    model = SkillCategory


class StageRepository(BaseRepository):
    model = Stage


class StageVersionRepository(BaseRepository):
    model = StageVersion
