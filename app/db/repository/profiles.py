from sqlalchemy import select, update, func, or_, and_, outerjoin
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Department, DepartmentProfile
from db.repository.base import BaseRepository
from db.models.users import User
from db.models.profiles import Profile, ProfileLevel
from db.models.skills import LevelSkill, Skill


class ProfileRepository(BaseRepository):
    model = Profile

    def __init__(self, session: AsyncSession):
        self.level_repository = None
        self.level_skill_repository = None
        super().__init__(session)

    async def get_list(self, filter_dict: dict, department_ids: list[int] | None):
        stmt = select(Profile)

        stmt = stmt.filter_by(**filter_dict)

        if department_ids is not None:
            stmt = stmt.where(
                Profile.is_active == True,
                Profile.departments.has(Department.id.in_(department_ids)),
            )

        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def accessible_profiles(self, department_ids: list[int] | None = None):
        stmt = select(Profile.id)
        if department_ids is not None:
            stmt = stmt.where(
                Profile.is_active == True,
                Profile.departments.has(Department.id.in_(department_ids)),
            )
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def get_profile_levels(self, profile_id: int):
        stmt = (
            select(Profile)
            .where(Profile.id == profile_id)
            .options(selectinload(Profile.levels))
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_profiles_by_department(self, department_id: int):
        stmt = (
            select(Profile)
            .distinct()
            .join(Profile.users)
            .where(User.department_id == department_id)
        )
        res = await self._session.execute(stmt)
        return res.scalars().unique().all()

    async def get_profiles_with_levels(
        self,
        profile_id: int | None = None,
        department_ids: list[int] | None = None,
    ):
        stmt = select(Profile)
        if profile_id:
            stmt = select(Profile).where(Profile.id == profile_id)
        if department_ids:
            stmt = stmt.where(
                Profile.is_active == True,
                Profile.departments.has(Department.id.in_(department_ids)),
            )
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
                joinedload(Profile.departments).load_only(
                    Department.id,
                    Department.department_name,
                ),
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
        stmt = select(func.count(LevelSkill.id)).where(LevelSkill.profile_level_id == profile_level_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()



