from sqlalchemy import select, func
from sqlalchemy.orm import contains_eager, selectinload

from db.models import (
    ProfileLevel,
    Profile,
    DepartmentProfile,
    Skill,
    Category,
    SkillCategory,
    Stage,
    LevelSkill,
    StageVersion,
    StageQuestion,
)
from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler


class SkillRepository(BaseRepository):
    model = Skill

    @db_exception_handler
    async def get_list_by_categories(self, categories: list[int]):
        stmt = select(Skill).where(Skill.is_active.is_(True))
        if categories:
            stmt = stmt.join(SkillCategory, SkillCategory.skill_id == Skill.id).where(
                SkillCategory.category_id.in_(categories)
            )
        res = await self._session.execute(stmt)
        return res.unique().scalars().all()

    @db_exception_handler
    async def get_all_by_categories(self, categories: list[int] | None = None):

        stmt = (
            select(Skill)
            .where(Skill.is_active.is_(True))
            .options(selectinload(Skill.stages))
        )
        if categories:
            stmt = stmt.join(Skill.categories.in_(categories)).options(
                contains_eager(Skill.categories).load_only(
                    Category.id, Category.category_name
                )
            )
        else:
            stmt = stmt.options(selectinload(Skill.categories))
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
            .options(contains_eager(Skill.stages).contains_eager(Stage.stage_versions))
        )

        res = await self._session.execute(stmt)

        if skill_id is not None:
            return res.unique().scalar_one_or_none()
        return res.unique().scalars().all()

    @db_exception_handler
    async def skill_exist(self, skill_id: int, departments_id: list[int]):
        stmt = (
            select(Skill.id)
            .join(LevelSkill, LevelSkill.skill_id == Skill.id)
            .join(ProfileLevel, ProfileLevel.id == LevelSkill.profile_level_id)
            .join(Profile, Profile.id == ProfileLevel.profile_id)
            .join(DepartmentProfile, DepartmentProfile.profile_id == Profile.id)
            .where(
                Skill.id == skill_id,
                DepartmentProfile.department_id.in_(departments_id),
                Profile.is_active.is_(True),
                ProfileLevel.is_active.is_(True),
            )
            .limit(1)
        )

        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_last_skill_with_questions(self, skill_id: int):
        last_version = self.get_last_version()
        stmt = (
            select(Skill)
            .where(Skill.id == skill_id, Skill.is_active.is_(True))
            .outerjoin(Skill.stages.and_(Stage.is_active.is_(True)))
            .outerjoin(last_version, last_version.c.stage_id == Stage.id)
            .outerjoin(
                StageVersion,
                (StageVersion.stage_id == Stage.id)
                & (StageVersion.version == last_version.c.version),
            )
            .outerjoin(StageQuestion, StageQuestion.stage_version_id == StageVersion.id)
            .options(
                contains_eager(Skill.stages)
                .contains_eager(Stage.stage_versions)
                .joinedload(StageVersion.questions),
                selectinload(Skill.categories),
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






