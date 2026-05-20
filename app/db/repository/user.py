from sqlalchemy.orm import joinedload
from sqlalchemy import select
from db.repository.decorators import db_exception_handler
from db.repository import BaseRepository
from db.models import User, Role, Department

class UserRepository(BaseRepository):
    model = User

    @db_exception_handler
    async def get_all(self, filter_dict: dict):
        departments_id = filter_dict.pop("departments_id", None)
        stmt = (
            select(
                User
            ).filter_by(**filter_dict)
            .options(
                joinedload(User.role),
                        joinedload(User.department),
                        joinedload(User.managed_division),
                        joinedload(User.managed_department))
        )
        if departments_id:
            stmt = stmt.where(User.department.has(Department.id.in_(departments_id)))
        res = await self._session.execute(stmt)
        return res.scalars().all()

    @db_exception_handler
    async def get_user_role(self, user_filter: dict, department_ids: list[int] | None = None):
        stmt = select(User).filter_by(**user_filter)

        if department_ids:
            stmt = stmt.where(User.department_id.has(Department.id.in_(department_ids)))

        stmt = (
            select(User)
            .filter_by(**user_filter)
            .options(
                joinedload(User.role),
                joinedload(User.department),
                joinedload(User.managed_division)
            )
        )
        res = await self._session.execute(stmt)
        user = res.scalar_one_or_none()
        return user

    @db_exception_handler
    async def get_user_info(self, user_id: int):
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                joinedload(User.department),
                joinedload(User.role),
            )
        )
        res = await self._session.execute(stmt)
        user = res.scalar_one_or_none()
        return user


class RoleRepository(BaseRepository):
    model = Role
