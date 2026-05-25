from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.models import User, Role, Department
from db.repository import BaseRepository
from db.repository.decorators import db_exception_handler


class UserRepository(BaseRepository):
    model = User

    @db_exception_handler
    async def get_all(self, filter_dict: dict):
        departments_id = filter_dict.pop("departments_id", None)
        stmt = (
            select(User)
            .filter_by(**filter_dict)
            .options(
                joinedload(User.role),
                joinedload(User.department),
                joinedload(User.managed_division),
                joinedload(User.managed_department),
            )
        )
        if departments_id:
            stmt = stmt.where(User.department.has(Department.id.in_(departments_id)))
        res = await self._session.execute(stmt)
        return res.scalars().all()

    @db_exception_handler
    async def get_user_role(self, user_id: int):
        stmt = select(User).where(User.id == user_id).options(joinedload(User.role))
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_user_info(self, user_id: int | None, email: int | None):
        stmt = select(User)

        if user_id is not None:
            stmt = stmt.where(User.id == user_id)
        if email is not None:
            stmt = stmt.where(User.email == email)

        stmt = stmt.options(
            joinedload(User.role),
            joinedload(User.department),
            joinedload(User.managed_division),
            joinedload(User.managed_department),
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()


class RoleRepository(BaseRepository):
    model = Role
