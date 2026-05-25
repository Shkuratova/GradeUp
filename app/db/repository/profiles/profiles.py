from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, contains_eager

from db.models import (
    Department,
    DepartmentProfile,
    Profile,
    ProfileLevel,
    LevelSkill,
    Skill,
    Stage,
)
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

    @db_exception_handler
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


