from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession
from db.repository.base import BaseRepository
from db.models.users import  User
from db.models.profiles import Profile, ProfileLevel, ProfileLevelVersion
from db.models.skills import LevelSkill, Skill


class ProfileRepository(BaseRepository):
    model = Profile

    def __init__(self, session: AsyncSession):
        self.level_repository = None
        self.level_skill_repository = None
        super().__init__(session)

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
            select(Profile).distinct()
            .join(Profile.users)
            .where(User.department_id == department_id)
        )
        res = await self._session.execute(stmt)
        return res.scalars().unique().all()

    async def get_profiles_with_latest_levels(self, profile_id: int | None = None):
        last_versions = (
            select(
                ProfileLevelVersion.profile_level_id,
                func.max(ProfileLevelVersion.version).label("last_version"),
            )
            .group_by(ProfileLevelVersion.profile_level_id)
            .subquery()
        )
        stmt = select(Profile)

        if profile_id is not None:
            stmt = stmt.where(Profile.id == profile_id)


        stmt = (
            stmt
            .outerjoin(Profile.levels)
            .where(func.coalesce(ProfileLevel.is_active, True) == True)
            .outerjoin(
                last_versions, last_versions.c.profile_level_id == ProfileLevel.id
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
                .load_only(Skill.id, Skill.title)
            )
            .order_by(ProfileLevel.num)
        )

        res = await self._session.execute(stmt)
        if profile_id is not None:
            return res.scalars().unique().first()
        return res.unique().scalars().all()



class LevelRepository(BaseRepository):
    model = ProfileLevel



    async def add_level_with_skills(self, level_dict: dict):
        for lvl in level_dict["levels"]:
            level = ProfileLevel(level=lvl["level"])
            skill_ids = lvl["skills"]
            for skill_id in skill_ids:
                level_skill = LevelSkill(skill_id=skill_id)
                level.skills.append(level_skill)
            self._session.add(level)

class LevelVersionRepository(BaseRepository):
    model = ProfileLevelVersion
