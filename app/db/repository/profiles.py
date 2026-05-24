from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload, joinedload, contains_eager

from db.models import Department, DepartmentProfile, UserProfile
from db.models.profiles import Profile, ProfileLevel
from db.models.skills import LevelSkill, Skill, Stage
from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler


class ProfileRepository(BaseRepository):
    model = Profile

    @db_exception_handler
    async def get_list(self, filter_dict: dict):
        stmt = select(Profile)
        departments_id = filter_dict.pop("departments_id", None)
        stmt = stmt.filter_by(**filter_dict)

        if departments_id is not None:
            stmt = stmt.where(
                Profile.is_active == True,
                Profile.departments.has(Department.id.in_(departments_id)),
            )

        res = await self._session.execute(stmt)
        return res.scalars().all()

    @db_exception_handler
    async def profile_exist(self, profile_id: int, department_ids: list[int]):
        stmt = (
            select(Profile.id)
            .join(DepartmentProfile, DepartmentProfile.profile_id == Profile.id)
            .where(
                Profile.id == profile_id,
                Profile.is_active.is_(True),
                DepartmentProfile.department_id.in_(department_ids),
            )
            .limit(1)
        )

        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_profile_levels(self, profile_id: int):
        stmt = (
            select(Profile)
            .where(Profile.id == profile_id)
            .options(selectinload(Profile.levels))
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_profiles_with_levels(
        self, profile_id: int | None = None, departments_id: list[int] | None = None
    ):
        stmt = select(Profile).where(Profile.is_active.is_(True))
        if profile_id:
            stmt = stmt.where(
                Profile.id == profile_id,
            )
        if departments_id:
            stmt = stmt.where(
                Profile.departments.has(Department.id.in_(departments_id))
            )
        stmt = (
            stmt.outerjoin(Profile.levels.and_(ProfileLevel.is_active.is_(True)))
            .outerjoin(ProfileLevel.skills)
            .outerjoin(LevelSkill.skill)
            .options(
                contains_eager(Profile.levels)
                .contains_eager(ProfileLevel.skills)
                .contains_eager(LevelSkill.skill)
                .load_only(Skill.id, Skill.title),
            )
            .order_by(ProfileLevel.num)
        )

        res = await self._session.execute(stmt)
        if profile_id:
            return res.unique().scalar_one_or_none()
        return res.unique().scalars().all()

    async def get_profile_structure_by_id(self, profile_id: int):
        stmt = (
            select(Profile)
            .where(Profile.id == profile_id)
            .options(
                selectinload(Profile.levels)
                .load_only(
                    ProfileLevel.id,
                    ProfileLevel.num,
                    ProfileLevel.level_name,
                )
                .selectinload(ProfileLevel.skill_list)
                .load_only(
                    Skill.id,
                    Skill.title,
                )
                .selectinload(Skill.stages)
                .load_only(
                    Stage.id,
                    Stage.confirmation_type,
                )
            )
        )

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()


class LevelRepository(BaseRepository):
    model = ProfileLevel

    async def get_last_level_by_num(self, profile_id: int, level_num: int):

        stmt = select(ProfileLevel).where(
            ProfileLevel.profile_id == profile_id,
            ProfileLevel.is_active.is_(True),
            ProfileLevel.num == level_num,
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

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
                selectinload(ProfileLevel.skill_list).load_only(Skill.id, Skill.title)
                .selectinload(Skill.stages).load_only(Stage.id, Stage.confirmation_type)
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

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

