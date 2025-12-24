from app.db import BaseDAO
from pydantic import BaseModel
from app.auth.schemas import UserInfo
from .models import User, Role, Department, Position
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import ForbiddenException


class UserDAO(BaseDAO):
    model = User

    async def get_user_list_by_role(
        self, user_data: UserInfo, filters: BaseModel | None = None
    ) -> list[User]:
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        stmt = (
            select(User)
            .filter_by(**filter_dict)
            .options(
                joinedload(User.position),
                joinedload(User.department),
                joinedload(User.role),
            )
        )
        if user_data.role_id == 2:
            if user_data.department_id is None:
                raise ForbiddenException
            stmt = stmt.where(User.department_id == user_data.department_id)
        try:
            res = await self._session.execute(stmt)
            rows = res.scalars().all()
            return rows
        except SQLAlchemyError as e:
            print(e)
            raise


class DepartmentDAO(BaseDAO):
    model = Department


class RoleDAO(BaseDAO):
    model = Role


class PositionDAO(BaseDAO):
    model = Position
