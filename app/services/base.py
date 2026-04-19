from typing import Type

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from db.repository import BaseRepository
from exceptions.common import (
    NotFoundException,
    AlreadyExistException,
    DataValidationError,
)


class BaseService:
    entity_name = "Object"
    unique_fields = None
    repository_factory: Type[BaseRepository] = BaseRepository


    def __init__(self, session: AsyncSession):
        self.session = session

    @classmethod
    async def check_unique_constrain(cls, repository: BaseRepository, filter_dict: dict):
        filters = {
            unq: filter_dict.get(unq, None)
            for unq in cls.unique_fields
            if filter_dict.get(unq, None) is not None
        }
        if cls.unique_fields is not None and filters:
            object_exist = await repository.get_one_by_filter(filters)
            if object_exist is not None:
                raise AlreadyExistException(
                    f"""{cls.entity_name} с {", ".join(f'{k} = {v}' for k, v in filters.items())} уже существует."""
                )

    async def get_by_id(self, object_id: int):
        repository: BaseRepository = self.repository_factory(self.session)
        instance = await repository.get_by_id(object_id)
        if instance is None:
            raise NotFoundException(f"{self.entity_name} c id = {object_id} не найден.")
        return instance

    async def get_all(self, filter_model: BaseModel | None = None):
        filter_dict = (
            {} if filter_model is None else filter_model.model_dump(exclude_none=True)
        )
        repository: BaseRepository = self.repository_factory(self.session)
        return await repository.get_all(filter_dict)

    async def update_by_id(self, object_id: int, object_model: BaseModel):
        object_dict = object_model.model_dump(exclude_none=True)
        if not object_dict:
            raise DataValidationError(
                "Хотя бы одно поле для обновления должно быть передано."
            )
        repository: BaseRepository = self.repository_factory(self.session)
        if self.unique_fields:
            await self.check_unique_constrain(repository, object_dict)
        res = await repository.update_by_id(object_id, object_dict)
        if not res:
            raise NotFoundException(
                f"{self.entity_name} c id = {object_id} не найден."
            )

    async def delete_by_id(self, object_id: int):
        repository: BaseRepository = self.repository_factory(self.session)
        res = await repository.delete_by_id(object_id)
        if not res:
            raise NotFoundException(f"{self.entity_name} c id = {object_id} не найден.")

    async def add(self, object_model: BaseModel):
        object_dict = object_model.model_dump(exclude_none=True)
        repository: BaseRepository = self.repository_factory(self.session)
        if self.unique_fields:
            await self.check_unique_constrain(repository, object_dict)
        return await repository.add(object_dict)
