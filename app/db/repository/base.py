import logging
logger = logging.getLogger(__name__)


from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import Base
from db.repository.decorators import db_exception_handler


class BaseRepository:

    model = Base

    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    @db_exception_handler
    async def get_by_id(self, data_id: int):
        stmt = select(self.model).where(self.model.id == data_id)
        res = await self._session.execute(stmt)

        logger.info(
            "Получен объект (%s) по id из таблицы (data_id=%s)",
            self.model.__name__,
            data_id,
        )
        return res.scalar_one_or_none()

    @db_exception_handler
    async def get_all(self, filter_dict: dict | None = None):
        if filter_dict is None:
            filter_dict = {}
        stmt = select(self.model).filter_by(**filter_dict)
        res = await self._session.execute(stmt)

        logger.info("Получен список объектов таблицы (%s)", self.model.__name__)
        return res.scalars().all()

    @db_exception_handler
    async def add(self, value_dict: dict):
        new_instance = self.model(**value_dict)
        self._session.add(new_instance)
        await self._session.flush()
        logger.info("Добавлен объект в таблицу (%s)", self.model.__name__)
        return new_instance

    @db_exception_handler
    async def add_list(self, values: list[dict]):
        await self._session.execute(
            insert(self.model),
            values,
        )
        logger.info("Добавлен список объекто в таблицу (%s)", self.model.__name__)

    @db_exception_handler
    async def get_one_by_filter(self, filter_dict: dict):
        stmt = select(self.model).filter_by(**filter_dict)
        res = await self._session.execute(stmt)

        logger.info(
            "Получен объект по фильтрам из таблицы (%s)", self.model.__name__
        )
        return res.scalar_one_or_none()

    @db_exception_handler
    async def exists(self, filter_dict: dict) -> bool:
        stmt = select(self.model.id).filter_by(**filter_dict).limit(1)
        res = await self._session.execute(stmt)

        logger.info(
            "Проверка существования объекта по фильтрам из таблицы (%s)",
            self.model.__name__,
        )
        return res.scalar_one_or_none() is not None

    @db_exception_handler
    async def update_by_id(self, data_id: int, value_dict: dict) -> int:
        stmt = update(self.model).where(self.model.id == data_id).values(**value_dict)
        res = await self._session.execute(stmt)
        logger.info(
            "Обновлен объект из таблицы (%s) по id (data_id=%s)",self.model.__name__,data_id,
        )
        return res.rowcount

    @db_exception_handler
    async def delete_by_id(self, data_id: int):
        stmt = delete(self.model).where(self.model.id == data_id)
        res = await self._session.execute(stmt)
        logger.info(
            "Получен объект по фильтрам из таблицы (%s)", self.model.__name__
        )
        return res.rowcount

    @db_exception_handler
    async def soft_delete_by_id(self, data_id: int):
        stmt = (
            update(self.model)
            .where(self.model.id == data_id)
            .values({"is_active": False})
        )
        res = await self._session.execute(stmt)
        return res.rowcount

    @db_exception_handler
    async def delete_list(self, data_ids: list[int]):
        stmt = delete(self.model).where(self.model.id.in_(data_ids))
        res = await self._session.execute(stmt)
        logger.info(
            "Удален список объектов с заданными ids из таблицы (%s)", self.model.__name__
        )
        return res.rowcount

    @db_exception_handler
    async def soft_delete_list(self, data_ids: list[int]):
        stmt = (
            update(self.model)
            .where(self.model.id.in_(data_ids))
            .values({"is_active": False})
        )
        res = await self._session.execute(stmt)
        return res.rowcount
