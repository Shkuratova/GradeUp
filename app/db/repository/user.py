from sqlalchemy.orm import joinedload
from sqlalchemy import select
from db.repository.decorators import db_exception_handler
from db.repository.base import BaseRepository
from db.models import User, Role
from pydantic import BaseModel


class UserRepository(BaseRepository):
    model = User

    @db_exception_handler
    async def get_all(self, user_filter: dict):
        stmt = (
            select(
                User
            ).filter_by(**user_filter)
            .options(joinedload(User.role), joinedload(User.department))
        )
        res = await self._session.execute(stmt)
        return res.scalars()

    @db_exception_handler
    async def get_user_role(self, user_filter: dict):
        stmt = (
            select(
                User.id,
                User.password,
                User.email,
                User.first_name,
                User.last_name,
                User.patronymic,
                User.department_id,
                Role.role_name,
            )
            .filter_by(**user_filter)
            .join(Role, Role.id == User.role_id)
        )
        res = await self._session.execute(stmt)
        row = res.fetchone()
        return row

    @db_exception_handler
    async def get_user_info(self, user_id: int):
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                joinedload(User.position),
                joinedload(User.department),
                joinedload(User.role),
            )
        )
        res = await self._session.execute(stmt)
        user = res.scalar_one_or_none()
        return user



def user_repository_factory(session):
    return UserRepository(session)