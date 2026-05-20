from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload, contains_eager

from db.models import Department, DepartmentProfile
from db.models.profiles import Profile, ProfileLevel
from db.models.skills import LevelSkill, Skill
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
    async def get_profiles_with_levels(self, profile_id: int | None = None):
        stmt = select(Profile)
        if profile_id:
            stmt = select(Profile).where(Profile.id == profile_id)
        stmt = (
            stmt.outerjoin(Profile.levels)
            .where(func.coalesce(ProfileLevel.is_active, True).is_(True))
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


class LevelRepository(BaseRepository):
    model = ProfileLevel

    async def get_last_level_by_num(self, profile_id: int, level_num: int):

        stmt = select(ProfileLevel.id).where(
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
