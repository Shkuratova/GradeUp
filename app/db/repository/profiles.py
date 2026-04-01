from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from db.repository.base import BaseRepository
from db.models import Profile, ProfileLevel, User


class ProfileRepository(BaseRepository):
    model = Profile

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


class ProfileLevelRepository(BaseRepository):
    model = ProfileLevel


def profile_repository_factory(session):
    return ProfileRepository(session)


def level_repository_factory(session):
    return ProfileLevelRepository(session)
