from sqlalchemy import select, update, func, or_, and_, outerjoin
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Department
from db.repository.base import BaseRepository
from db.models.users import User
from db.models.profiles import Profile, ProfileLevel, ProfileLevelVersion
from db.models.skills import LevelSkill, Skill


class ProfileRepository(BaseRepository):
    model = Profile

    def __init__(self, session: AsyncSession):
        self.level_repository = None
        self.level_skill_repository = None
        super().__init__(session)

    async def get_list(self, filter_dict: dict, department_id: int | None):
        stmt = select(Profile)

        stmt = stmt.filter_by(**filter_dict)

        if department_id is not None:
            stmt = stmt.where(
                and_(
                    Profile.is_active == True,
                    or_(
                        Profile.department_id.is_(None),
                        Profile.department_id == department_id,
                    ),
                )
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

    async def get_profiles_with_latest_levels(
        self,
        profile_id: int | None = None,
        department_id: int | None = None,
    ):
        last_versions = (
        select(
            ProfileLevelVersion.profile_level_id,
            func.max(ProfileLevelVersion.version).label("last_version"),
        )
        .group_by(ProfileLevelVersion.profile_level_id)
        .subquery()
        )

        stmt = (
            select(Profile)
            .where(Profile.id == profile_id)
        )

        if department_id is not None:
            stmt = stmt.where(
                or_(
                    Profile.department_id == department_id,
                    Profile.department_id.is_(None),
                )
            )

        stmt = (
            stmt.outerjoin(Profile.levels)
            .where(func.coalesce(ProfileLevel.is_active, True).is_(True))
            .outerjoin(
                last_versions,
                last_versions.c.profile_level_id == ProfileLevel.id,
            )
            .outerjoin(
                ProfileLevelVersion,
                (ProfileLevelVersion.profile_level_id == ProfileLevel.id)
                & (ProfileLevelVersion.version == last_versions.c.last_version),
            )
            .outerjoin(ProfileLevelVersion.skills)
            .outerjoin(LevelSkill.skill)
            .options(
                contains_eager(Profile.levels)
                .contains_eager(ProfileLevel.versions)
                .contains_eager(ProfileLevelVersion.skills)
                .contains_eager(LevelSkill.skill)
                .load_only(Skill.id, Skill.title),
                joinedload(Profile.department).load_only(
                    Department.id,
                    Department.department_name,
                ),
            )
            .order_by(ProfileLevel.num)
        )

        res = await self._session.execute(stmt)
        return res.unique().scalar_one_or_none()

class LevelRepository(BaseRepository):
    model = ProfileLevel

    async def get_last_level_by_num(self, profile_id: int, level_num: int):


        stmt = (
            select(ProfileLevel.id)
            .where(
                ProfileLevel.profile_id == profile_id,
                ProfileLevel.is_active.is_(True),
                ProfileLevel.num == level_num
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

class LevelVersionRepository(BaseRepository):
    model = ProfileLevelVersion
