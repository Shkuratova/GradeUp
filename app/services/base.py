import logging
logger = logging.getLogger(__name__)

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.common import (
    NotFoundException,
    AlreadyExistException,
    DataValidationError,
)


class BaseService:
    entity_name = "Object"
    unique_fields = None

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = None

    async def check_unique_constraint(
        self,
        filter_dict: dict,
        object_id: int | None = None,
    ):
        if not self.unique_fields:
            return

        filters = {
            field: filter_dict[field]
            for field in self.unique_fields
            if filter_dict.get(field) is not None
        }

        if not filters:
            return

        object_exist = await self.repository.get_one_by_filter(filters)

        if object_exist is None:
            return

        if object_id is not None and object_exist.id == object_id:
            return

        logger.warning(
            "Нарушение уникальности для %s: %s",
            self.entity_name,
            filters,
        )
        raise AlreadyExistException(
            f"{self.entity_name} с "
            f'{", ".join(f"{k}={v.__repr__()}" for k, v in filters.items())} '
            f"уже существует."
        )

    async def get_by_id(self, object_id: int):
        instance = await self.repository.get_by_id(object_id)
        if instance is None:
            raise NotFoundException( f"{self.entity_name} с id={object_id} не найден.")
        return instance

    async def get_all(self, filter_model: BaseModel | None = None):
        filter_dict = (
            {} if filter_model is None else filter_model.model_dump(exclude_none=True)
        )
        return await self.repository.get_all(filter_dict)

    async def update_by_id(self, object_id: int, object_model: BaseModel):
        object_dict = object_model.model_dump(exclude_none=True)
        if not object_dict:
            raise DataValidationError(
                "Хотя бы одно поле для обновления должно быть передано."
            )

        if self.unique_fields:
            await self.check_unique_constraint(object_dict, object_id)
        res = await self.repository.update_by_id(object_id, object_dict)
        if not res:
            raise NotFoundException(
                f"{self.entity_name} c id = {object_id} не найден."
            )
        return self.get_by_id(object_id)

    async def delete_by_id(self, object_id: int):
        res = await self.repository.delete_by_id(object_id)
        if not res:
            raise NotFoundException(f"{self.entity_name} c id = {object_id} не найден.")

    async def soft_delete_by_id(self, object_id: int):
        res = await self.repository.soft_delete_by_id(object_id)
        if not res:
            raise NotFoundException(f"{self.entity_name} c id = {object_id} не найден.")

    async def add(self, object_model: BaseModel):
        object_dict = object_model.model_dump(exclude_none=True)

        if self.unique_fields:
            await self.check_unique_constraint(object_dict)
        return await self.repository.add(object_dict)
