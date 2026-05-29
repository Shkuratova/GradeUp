from sqlalchemy import select

from db.models import User, Role, Department
from db.models.departments import DepartmentUser, Division
from db.repository import BaseRepository
from db.repository.decorators import db_exception_handler

import logging
logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    model = User

    @staticmethod
    def _user_query():
        stmt = (
            select(
                User.id,
                User.email,
                User.password,
                User.first_name,
                User.last_name,
                User.patronymic,
                User.position,
                User.role_id,
                Role.role_name,
                DepartmentUser.department_id,
                Department.department_name,
                DepartmentUser.role.label("department_role"),
                Division.id.label("managed_division_id"),
                Division.division_name.label("managed_division_name"),
            )
            .join(Role, Role.id == User.role_id)
            .outerjoin(DepartmentUser, DepartmentUser.user_id == User.id)
            .outerjoin(Department, Department.id == DepartmentUser.department_id)
            .outerjoin(Division, Division.supervisor_id == User.id)
        )
        return stmt
    @db_exception_handler
    async def get_all(self, filter_dict: dict):
        departments_id = filter_dict.pop("departments_id", None)
        stmt = self._user_query()
        if departments_id:
            stmt = stmt.where(
                User.department_role.has(
                    DepartmentUser.department_id.in_(departments_id)
                )
            )

        res = await self._session.execute(stmt)

        logger.info("Выполнен запрос на получение списка пользователей по фильтрам")
        return res.mappings().all()

    @db_exception_handler
    async def get_user_info(self, user_id: int | None, email: str | None = None):
        stmt = self._user_query()

        if user_id is not None:
            stmt = stmt.where(User.id == user_id)
        if email is not None:
            stmt = stmt.where(User.email == email)

        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение информации о пользователе по id или email (user_id=%s, email=%s)",
            user_id,
            email,
        )
        return res.mappings().one_or_none()


class RoleRepository(BaseRepository):
    model = Role
