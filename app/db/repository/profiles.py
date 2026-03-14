from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.repository.base import BaseRepository
from db.models import Profile, ProfileLevel, Level


class ProfileRepository(BaseRepository):
    model = Profile

    async def get_profile_levels(self, profile_id: int):
        stmt = select(Profile).where(Profile.id == profile_id).options(selectinload(Profile.levels))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


class LevelRepository(BaseRepository):
    model = Level


class ProfileLevelRepository(BaseRepository):
    model = ProfileLevel


def profile_repository_factory(session):
        return ProfileRepository(session)

def level_repository_factory(session):
    return LevelRepository(session)

def profile_level_repository_factory(session):
    return ProfileLevelRepository(session)
