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
        return res.scalars().all()

    @db_exception_handler
    async def get_user_role(self, user_filter: dict):
        stmt = (
            select(User)
            .filter_by(**user_filter)
            .options(joinedload(User.role))
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



