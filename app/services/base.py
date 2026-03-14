from pydantic import BaseModel
from db.repository import BaseRepository
from db.uow import unit_of_work
from exceptions.common import NotFoundException, AlreadyExistException
from exceptions.user import UserException


class BaseService:
    entity_name = "Object"

    def __init__(self, repository_factory):
        self.repository_factory = repository_factory

    async def get_by_id(self, object_id:int):
        async with unit_of_work() as uow:
            repository: BaseRepository = self.repository_factory(uow.session)
            instance =  await repository.get_by_id(object_id)
        if instance is None:
            raise NotFoundException(f"{self.entity_name} c id = {object_id} не найден.")
        return instance

    async def get_all(self, filter_model: BaseModel | None = None):
        print("ENTITY:", self.entity_name)
        filter_dict = {} if filter_model is None else filter_model.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            repository: BaseRepository = self.repository_factory(uow.session)
            return await repository.get_all(filter_dict)

    async def update_by_id(self, object_id: int, data: BaseModel):
        data_dict = data.model_dump(exclude_none=True)
        if not data_dict:
            raise UserException("Хотя бы одно поле для обновления должно быть передано.")
        async with unit_of_work() as uow:
            repository: BaseRepository = self.repository_factory(uow.session)
            res = await repository.update_by_id(object_id, data_dict)
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

