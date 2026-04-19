from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from db.repository.base import BaseRepository
from db.models import Profile, ProfileLevel, User, LevelSkill


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
            select(Profile)
            .distinct()
            .join(Profile.users)
            .where(User.department_id == department_id)
        )
        res = await self._session.execute(stmt)
        return res.scalars().unique().all()

    async def get_profile_with_details(self, profile_id: int):
        stmt = (
            select(Profile)
            .where(Profile.id == profile_id)
            .options(
                selectinload(Profile.levels)
                .selectinload(ProfileLevel.skills)
                .selectinload(LevelSkill.skill)
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


class ProfileLevelRepository(BaseRepository):
    model = ProfileLevel

    async def add_level_with_skills(self, level_dict: dict):
        for lvl in level_dict["levels"]:
            level = ProfileLevel(level=lvl["level"])
            skill_ids = lvl["skills"]
            for skill_id in skill_ids:
                level_skill = LevelSkill(skill_id=skill_id)
                level.skills.append(level_skill)
            self._session.add(level)
