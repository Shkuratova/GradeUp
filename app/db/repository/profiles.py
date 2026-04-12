from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from db.repository.base import BaseRepository
from db.models import Profile, ProfileLevel, User
from db.repository.skill import LevelSkillRepository


class ProfileRepository(BaseRepository):
    model = Profile

    def __init__(self, session: AsyncSession):
        self.level_repository = None
        self.level_skill_repository = None
        super().__init__(session)

    @property
    def level_repository(self):
        if self.level_repository is None:
            self.level_repository = ProfileLevelRepository(self._session)
        return self.level_repository

    @property
    def level_skill_repository(self):
        if self.level_skill_repository is None:
            self.level_skill_repository = LevelSkillRepository(self._session)
        return self.level_skill_repository

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

    @level_repository.setter
    def level_repository(self, value):
        self._level_repository = value

    @level_skill_repository.setter
    def level_skill_repository(self, value):
        self._level_skill_repository = value


class ProfileLevelRepository(BaseRepository):
    model = ProfileLevel


