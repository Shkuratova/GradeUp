from db.repository import LevelSkillRepository
from db.repository.profiles import (
    ProfileRepository,
    ProfileLevelRepository,
)
from exceptions.common import (
    NotFoundException,
    DataValidationError,
)
from schemas.profiles import (
    ProfileLevels,
    SProfileAdd,
    SProfile,
    SProfileUpdate,
)
from services.base import BaseService
from services.level import LevelService


class ProfileService(BaseService):

    entity_name = "Профиль"
    unique_fields = ["title"]
    repository_factory = ProfileRepository

    async def get_profile_levels(self, profile_id: int):
        repository = ProfileRepository(self.session)
        profile = await repository.get_profile_levels(profile_id)
        if profile is None:
            raise NotFoundException(f"Профиль с id = {profile_id} не найден.")
        return profile

    async def get_all_by_department_id(self, department_id: int):
        repository = ProfileRepository(self.session)
        profiles = await repository.get_profiles_by_department(department_id)
        return profiles

    async def get_with_details(self, profile_id: int):
        repository = ProfileRepository(self.session)
        profile = await repository.get_profile_with_details(profile_id)
        if profile is None:
            raise NotFoundException(
                f"{self.entity_name} c id = {profile_id} не найден."
            )
        return SProfile.model_validate(profile)

    async def add_profile(self, model: SProfileAdd):
        repository = ProfileRepository(self.session)
        profile = await repository.add(model.profile.model_dump())

        if model.levels:
            level_service = LevelService(self.session)
            await level_service.add_levels_with_skills(model.levels)

        return profile

    async def update_by_id(self, profile_id: int, profile: SProfileUpdate):
        repository: ProfileRepository = self.repository_factory(self.session)
        profile_old: SProfile = await self.get_with_details(profile_id)

        profile_update_data = profile.profile.model_dump(exclude_none=True)
        res = await repository.update_by_id(profile_id, profile_update_data)

        if profile.levels:
            level_service = LevelService(self.session)
            await level_service.update_levels_with_skills(profile_id, profile_old.levels, profile.levels)
        return res
