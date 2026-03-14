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
    unique_field = "position"

    async def get_profile_levels(self, profile_id: int):
        async with unit_of_work() as uow:
            repository: ProfileRepository = self.repository_factory(uow.session)
            profile = await repository.get_profile_levels(profile_id)
            if profile is None:
                raise NotFoundException(f"Профиль с id = {profile_id} не найден.")
        return profile


profile_service = ProfileService(profile_repository_factory)


class LevelService(BaseService):

    entity_name = "Уровень"
    unique_field = "name"


level_service = LevelService(level_repository_factory)
