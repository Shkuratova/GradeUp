from services.base import BaseService
from schemas.profiles import ProfileBase, LevelBase, ProfileAdd, LevelAdd
from db.uow import unit_of_work
from db.repository.profiles import (
    ProfileRepository,
    LevelRepository,
    profile_repository_factory,
    level_repository_factory,
)
from exceptions.common import AlreadyExistException, NotFoundException

class ProfileService(BaseService):

    entity_name = "Профиль"

    async def add(self, profile: ProfileAdd):
        profile_dict = profile.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            repository: ProfileRepository = self.repository_factory(uow.session)
            profile_exist = await repository.get_one_by_filter({"position": profile.position})
            if profile_exist is not None:
                raise AlreadyExistException(f"Профиль с названием {profile.position} уже существует")
            res = await repository.add(profile_dict)
            return res

    async def get_profile_levels(self, profile_id: int):
        async with unit_of_work() as uow:
            repository: ProfileRepository = self.repository_factory(uow.session)
            profile = await repository.get_profile_levels(profile_id)
            if profile is None:
                raise NotFoundException(f"Профиль с id = {profile_id} не найден." )
        return profile

profile_service = ProfileService(profile_repository_factory)

class LevelService(BaseService):

    entity_name = "Уровень"

    async def add(self, level: LevelAdd):
        level_dict = level.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            repository: LevelRepository = self.repository_factory(uow.session)
            level_exist = await repository.get_one_by_filter({"name": level.name})
            if level_exist is not None:
                raise AlreadyExistException(f"Уровень с названием {level.name} уже существует")
            res = await repository.add(level_dict)
            return res

level_service = LevelService(level_repository_factory)
