from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload

from db.models import Department, Division, DepartmentProfile, Profile, User
from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler


class DepartmentRepository(BaseRepository):
    model = Department

    @db_exception_handler
    async def get_detail(self, department_id):
        stmt = (
            select(Department)
            .where(Department.id == department_id)
            .options(
                joinedload(Department.supervisor).load_only(
                    User.id,
                    User.first_name,
                    User.last_name,
                    User.patronymic,
                    User.email,
                    User.department_id,
                ),
                selectinload(Department.profiles).load_only(Profile.id, Profile.title),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_departments_id(self, division_id: int | None = None):
        stmt = select(Department.id)
        if division_id:
            stmt = stmt.where(Department.division_id == division_id)
        res = await self._session.execute(stmt)
        return res.scalars().all()

    @db_exception_handler
    async def get_with_profiles(self, departments_id: list[int] | None = None):
        stmt = select(Department)
        if departments_id:
            stmt = stmt.where(Department.id.in_(departments_id))
        stmt = stmt.options(
            joinedload(Department.supervisor),
            selectinload(Department.profiles).load_only(Profile.id, Profile.title),
        )

        res = await self._session.execute(stmt)
        return res.scalars().all()

    @db_exception_handler
    async def get_supervisor(self, department_id: int):
        stmt = (
            select(Department)
            .where(Department.id == department_id)
            .options(joinedload(Department.supervisor).load_only(User.id))
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_id_by_division_id(self, division_id):
        stmt = select(Department.id).where(Department.division_id == division_id)
        res = await self._session.execute(stmt)
        return res.scalars().all()

    @db_exception_handler
    async def get_user_count(self, department_id):
        stmt = select(func.count(User.id)).where(User.department_id == department_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_by_ids(self, departments_id: list[int] | None):
        stmt = select(Department)
        if departments_id:
            stmt = stmt.where(Department.id.in_(departments_id))

        res = await self._session.execute(stmt)
        return res.scalars().all()


class DepartmentProfileRepository(BaseRepository):
    model = DepartmentProfile
