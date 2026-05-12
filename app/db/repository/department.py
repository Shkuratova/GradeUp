from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from db.repository.base import BaseRepository
from db.models import Department, Division, DepartmentProfile, Profile, User


class DivisionRepository(BaseRepository):
    model = Division

    async def get_division_detail(self, division_id):
        stmt = (
            select(Division)
            .where(Division.id == division_id)
            .options(
                selectinload(Division.departments),
                joinedload(Division.supervisor)
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


class DepartmentRepository(BaseRepository):
    model = Department

    async def get_detail(self, department_id):
        stmt = (
            select(Department)
            .where(Department.id == department_id)
            .options(
                joinedload(Department.supervisor).load_only(User.id, User.first_name, User.last_name, User.patronymic),
                selectinload(Department.profiles).load_only(Profile.id, Profile.title)
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


class DepartmentProfileRepository(BaseRepository):
    model = DepartmentProfile
