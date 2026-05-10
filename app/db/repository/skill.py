from sqlalchemy.orm import contains_eager, selectinload, with_loader_criteria, aliased
from sqlalchemy import select, delete, func
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
            .where(Skill.is_active == True)
            .join(Skill.categories)
            .where(Category.id.in_(categories))
            .options(contains_eager(Skill.categories).load_only(Category.id))
        )
        res = await self._session.execute(stmt)
        return res.unique().scalars().all()

    @classmethod
    def get_last_version(cls):
        last_versions = (
            select(
                StageVersion.stage_id,
                func.max(StageVersion.version).label("version"),
            )
            .group_by(StageVersion.stage_id)
            .subquery()
        )

        return (
            select(StageVersion)
            .join(
                last_versions,
                (StageVersion.stage_id == last_versions.c.stage_id)
                & (StageVersion.version == last_versions.c.version),
            )
            .subquery()
        )

    @db_exception_handler
    async def get_stages(self, filter_dict: dict, skill_id: int | None = None):
        category_ids = filter_dict.pop("categories", None)

        last_version = self.get_last_version()

        stmt = select(Skill)

        if skill_id is not None:
            stmt = stmt.where(Skill.id == skill_id)

        if category_ids:
            stmt = stmt.join(Skill.categories).where(Category.id.in_(category_ids))

        stmt = (
            stmt.outerjoin(Skill.stages)
            .where(func.coalesce(Stage.is_active, True) == True)
            .outerjoin(last_version, last_version.c.stage_id == Stage.id)
            .outerjoin(
                StageVersion,
                (StageVersion.stage_id == Stage.id)
                & (StageVersion.version == last_version.c.version),
            )
            .options(
                contains_eager(Skill.stages)
                .contains_eager(Stage.stage_versions)
            )
        )

        res = await self._session.execute(stmt)

        if skill_id is not None:
            return res.unique().scalar_one_or_none()
        return res.unique().scalars().all()

    @db_exception_handler
    async def get_last_skill_with_questions(self, skill_id: int):
        last_version = self.get_last_version()
        stmt = (
                select(Skill).where(Skill.id == skill_id)
                .join(Skill.stages)
                .where(Stage.is_active == True)
                .join(last_version, last_version.c.stage_id == Stage.id)
            .join(
                    StageVersion,
                    (StageVersion.stage_id == Stage.id)
                    & (StageVersion.version == last_version.c.version)
                )
            .join(StageQuestion, StageQuestion.stage_version_id == StageVersion.id)
            .options(
                    contains_eager(Skill.stages)
                    .contains_eager(Stage.stage_versions)
                    .joinedload(StageVersion.questions)
                )
            .order_by(StageQuestion.num)
        )
        res = await self._session.execute(stmt)
        return res.unique().scalar_one_or_none()

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



