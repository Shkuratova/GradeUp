from services.base import BaseService
from schemas.profiles import ProfileUpdate, ProfileLevels, SProfileAdd, SProfile
from db.uow import unit_of_work
from db.repository.profiles import (
    ProfileRepository,
    ProfileLevelRepository,
)
from db.repository.skill import SkillRepository, LevelSkillRepository
from db.uow import unit_of_work
from services.skill import SkillService
from services.skill import LevelSkillService
from exceptions.common import (
    AlreadyExistException,
    NotFoundException,
    DataValidationError,
)


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
            raise NotFoundException(f"{self.entity_name} c id = {profile_id} не найден.")
        return SProfile.model_validate(profile)

    async def add_profile(self, model: SProfileAdd):
        repository = ProfileRepository(self.session)
        profile = await repository.add(model.profile.model_dump())

        if not model.levels:
            return profile

        level_repo = ProfileLevelRepository(self.session)
        lvl_skill_repo = LevelSkillRepository(self.session)
        skill_repo = SkillRepository(self.session)

        all_skills = set()

        for lvl in model.levels:
            if lvl.skills:
                if any(skill in all_skills for skill in lvl.skills):
                    raise DataValidationError(
                        "Один навык не может входить в несколько уровней"
                    )
                all_skills.update(lvl.skills)

        if all_skills:
            existing_skills = await skill_repo.check_list(list(all_skills))
            existing_skills_set = set(existing_skills)

            if existing_skills_set != all_skills:
                missing = all_skills - existing_skills_set
                raise NotFoundException(
                    f"Навыки с id = [{', '.join(str(s) for s in missing)}] не найдены."
                )

        lvl_skills = []
        for lvl in model.levels:
            profile_level = await level_repo.add(
                {"profile_id": profile.id, "level": lvl.level}
            )

            if lvl.skills:
                lvl_skills.extend(
                    [
                        {"profile_level_id": profile_level.id, "skill_id": skill_id}
                        for skill_id in lvl.skills
                    ]
                )
        if lvl_skills:
            await lvl_skill_repo.add_list(lvl_skills)

        return profile


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
                lvl_add = [
                    lvl.model_dump(exclude_none=True)
                    for lvl in profile.levels
                    if lvl.id is None
                ]
                await level_repository.add_list(lvl_add)
                lvl_upd = [lvl for lvl in profile.levels if lvl.id]
                for l in lvl_upd:
                    await level_repository.update_by_id(
                        l.id, l.model_dump(exclude={"id"}, exclude_none=True)
                    )
                lvl_del = [
                    lvl.id for lvl in profile.levels if lvl.id not in profile_old.levels
                ]
                await level_repository.delete_list(lvl_del)


class LevelService(BaseService):

    entity_name = "Уровень"
    repository_factory = ProfileLevelRepository
