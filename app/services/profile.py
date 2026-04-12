from services.base import BaseService
from schemas.profiles import ProfileUpdate, ProfileLevels
from db.uow import unit_of_work
from db.repository.profiles import (
    ProfileRepository,
    ProfileLevelRepository,
    LevelSkillRepository,
)
from exceptions.common import AlreadyExistException, NotFoundException


class ProfileService(BaseService):

    entity_name = "Профиль"
    unique_fields = ["title"]
    repository_factory = ProfileRepository

    async def get_profile_levels(self, profile_id: int):
        async with unit_of_work() as uow:
            repository: ProfileRepository = self.repository_factory(uow.session)
            profile = await repository.get_profile_levels(profile_id)
            if profile is None:
                raise NotFoundException(f"Профиль с id = {profile_id} не найден.")
        return profile

    async def get_all_by_department_id(self, department_id: int):
        async with unit_of_work() as uow:
            repository: ProfileRepository = self.repository_factory(uow.session)
            profiles = await repository.get_profiles_by_department(department_id)
        return profiles

    async def update_by_id(self, profile_id: int, profile: ProfileUpdate):
        async with unit_of_work() as uow:
            repository: ProfileRepository = self.repository_factory(uow.sesion)
            profile_old: ProfileLevels = await repository.get_profile_levels(profile_id)
            if profile_old is None:
                raise NotFoundException(
                    f"{self.entity_name} с id = {profile_id} не найден."
                )

            value_dict = {}
            if profile.title is not None:
                value_dict["title"] = profile.title
            if profile.description is not None:
                value_dict["description"] = profile.description

            await repository.update_by_id(profile_id, value_dict)

            if profile.levels:
                level_repository = ProfileLevelRepository(uow.session)
                lvl_add = [lvl.model_dump(exclude_none=True) for lvl in profile.levels if lvl.id is None]
                await level_repository.add_list(lvl_add)
                lvl_upd = [lvl for lvl in profile.levels if lvl.id]
                for l in lvl_upd:
                    await level_repository.update_by_id(l.id, l.model_dump(exclude={"id"}, exclude_none=True))
                lvl_del = [lvl.id for lvl in profile.levels if lvl.id not in profile_old.levels]
                await level_repository.delete_list(lvl_del)


profile_service = ProfileService()


class LevelService(BaseService):

    entity_name = "Уровень"
    repository_factory = ProfileLevelRepository


level_service = LevelService()
