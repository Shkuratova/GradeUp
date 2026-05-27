from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload

from db.models import Department, Division, User
from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler

import logging
logger = logging.getLogger(__name__)


class DivisionRepository(BaseRepository):
    model = Division

    @db_exception_handler
    async def get_division_detail(self, division_id):
        stmt = (
            select(Division)
            .where(Division.id == division_id)
            .options(
                selectinload(Division.departments).load_only(
                    Department.id,
                    Department.department_name,
                    Department.description,
                    Department.supervisor_id,
                ),
                joinedload(Division.supervisor)
            )
        )
        res = await self._session.execute(stmt)

        logger.info("Выполнен запрос на получение Направления по id (division_id=%s)", division_id)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_department_cnt(self, division_id):
        stmt = select(func.count(Department.division_id)).where(
            Department.division_id == division_id
        )
        res = await self._session.execute(stmt)

        logger.info("Выполнен запрос на получение количества подчиненных отделов к Направлению (division_id=%s)", division_id)
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_with_departments(self):
        stmt = select(Division).options(
            selectinload(Division.departments).load_only(
                Department.id,
                Department.department_name,
                Department.description,
                Department.supervisor_id,
            ),
            joinedload(Division.supervisor),
        )
        res = await self._session.execute(stmt)

        logger.info("Выполнен запрос на получение Направлений с подчиненными отделами")
        return res.scalars().all()

