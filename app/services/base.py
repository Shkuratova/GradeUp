from pydantic import BaseModel
from db.repository import BaseRepository
from db.uow import unit_of_work
from exceptions.common import NotFoundException, AlreadyExistException, ValidationError


class BaseService:
    entity_name = "Object"
    unique_field = None

    def __init__(self, repository_factory):
        self.repository_factory = repository_factory

    async def get_by_id(self, object_id: int):
        async with unit_of_work() as uow:
            repository: BaseRepository = self.repository_factory(uow.session)
            instance = await repository.get_by_id(object_id)
        if instance is None:
            raise NotFoundException(f"{self.entity_name} c id = {object_id} не найден.")
        return instance

    async def get_all(self, filter_model: BaseModel | None = None):
        filter_dict = (
            {} if filter_model is None else filter_model.model_dump(exclude_none=True)
        )
        async with unit_of_work() as uow:
            repository: BaseRepository = self.repository_factory(uow.session)
            return await repository.get_all(filter_dict)

    async def update_by_id(self, object_id: int, object_model: BaseModel):
        object_dict = object_model.model_dump(exclude_none=True)
        if not object_dict:
            raise ValidationError("Хотя бы одно поле для обновления должно быть передано.")
        async with unit_of_work() as uow:
            repository: BaseRepository = self.repository_factory(uow.session)
            if self.unique_field is not None and object_dict.get(self.unique_field, None) is not  None:
                filters = {self.unique_field: object_dict[self.unique_field]}
                object_exist = await repository.get_one_by_filter(filters)
                if object_exist is not None:
                    raise AlreadyExistException(
                        f"{self.entity_name} с {self.unique_field} = {filters[self.unique_field]} уже существует."
                    )
            res = await repository.update_by_id(object_id, object_dict)
            if not res:
                raise NotFoundException(
                    f"{self.entity_name} c id = {object_id} не найден."
                )

    async def delete_by_id(self, object_id: int):
        async with unit_of_work() as uow:
            repository: BaseRepository = self.repository_factory(uow.session)
            res = await repository.delete_by_id(object_id)
        if not res:
            raise NotFoundException(f"{self.entity_name} c id = {object_id} не найден.")

    async def add(self, object_model: BaseModel):
        object_dict = object_model.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            repository: BaseRepository = self.repository_factory(uow.session)
            if self.unique_field is not None:
                filters = {self.unique_field: object_dict[self.unique_field]}
                object_exist = await repository.get_one_by_filter(filters)
                if object_exist is not None:
                    raise AlreadyExistException(
                        f"{self.entity_name} с {self.unique_field} = {filters[self.unique_field]} уже существует."
                    )
            return await repository.add(object_dict)
