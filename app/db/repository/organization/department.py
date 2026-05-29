import logging

logger = logging.getLogger(__name__)

from sqlalchemy import select, func, update
from sqlalchemy.orm import joinedload, selectinload

from db.models import (
    Department,
    DepartmentProfile,
    Profile,
    User,
    DepartmentUser,
)
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
                joinedload(Department.supervisor),
                selectinload(Department.profiles).load_only(Profile.id, Profile.title),
            )
        )
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение департамента по id (department_id=%s)"
        )
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_departments_id(self, division_id: int | None = None):
        stmt = select(Department.id)
        if division_id:
            stmt = stmt.where(Department.division_id == division_id)
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение списка id департаментов по id направления (division_id=%s)",
            division_id,
        )
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

        logger.info(
            "Выполнен запрос на получение списка департаментов с доступными профилями"
        )
        return res.scalars().all()

    @db_exception_handler
    async def get_supervisor(self, department_id: int):
        stmt = (
            select(Department)
            .where(Department.id == department_id)
            .options(joinedload(Department.supervisor).load_only(User.id))
        )
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение департамента (department_id=%s) с его руководителем",
            department_id,
        )
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_id_by_division_id(self, division_id):
        stmt = select(Department.id).where(Department.division_id == division_id)
        res = await self._session.execute(stmt)

        logger.info(
            "Выполнен запрос на получение id департаментов, привязанных к направлению  (division_id=%s)",
            division_id,
        )
        return res.scalars().all()


    @db_exception_handler
    async def get_by_ids(self, departments_id: list[int] | None):
        stmt = select(Department)
        if departments_id:
            stmt = stmt.where(Department.id.in_(departments_id))

        res = await self._session.execute(stmt)

        logger.info("Выполнен запрос на получение депаратаментов по списку id")
        return res.scalars().all()


class DepartmentProfileRepository(BaseRepository):
    model = DepartmentProfile


class DepartmentUserRepository(BaseRepository):
    model = DepartmentUser

    @db_exception_handler
    async def update_by_user_id(self, user_id: int, data: dict):
        stmt = (
            update(DepartmentUser)
            .where(DepartmentUser.user_id == user_id)
            .values(**data)
        )
        res = await self._session.execute(stmt)
        return res.rowcount

    @db_exception_handler
    async def get_user_count(self, department_id: int):
        stmt = select(func.count(DepartmentUser.id)).where(
            DepartmentUser.department_id == department_id
        )
        res = await self._session.execute(stmt)
        logger.info(
            "Выполнен запрос на получение количества сотрудников в отделе (department_id=%s)"
        )
        return res.scalar_one_or_none()
