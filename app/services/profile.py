from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import LevelSkillRepository
from db.repository.profiles import (
    ProfileRepository,
    LevelRepository,
    LevelVersionRepository,
)
from db.repository.skill import SkillRepository
from exceptions.common import (
    NotFoundException,
    DataValidationError,
)
from schemas.profiles import (
    ProfileLevels,
    SProfileAdd,
    SProfile,
    SProfileUpdate,
    SLevelAdd,
    SLevelUpdate,
)
from services.base import BaseService
from services.level import LevelService


class ProfileService(BaseService):

    entity_name = "Профиль"
    unique_fields = ["title"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = ProfileRepository(session)
        self.level_repository = LevelRepository(session)
        self.level_version_repository = LevelVersionRepository(session)
        self.level_skill_repository = LevelSkillRepository(session)
        self.skill_repository = SkillRepository(session)

    async def get_profile_levels(self, profile_id: int):
        profile = await self.repository.get_profile_levels(profile_id)
        if profile is None:
            raise NotFoundException(f"Профиль с id = {profile_id} не найден.")
        return profile

    async def get_all_by_department_id(self, department_id: int):
        profiles = await self.repository.get_profiles_by_department(department_id)
        return profiles

    async def get_with_details(self, profile_id: int):
        profile = await self.repository.get_profile_with_latest_levels(profile_id)

        if profile is None:
            raise NotFoundException(
                f"{self.entity_name} c id = {profile_id} не найден."
            )

        profile_dict = {
            "id": profile.id,
            "title": profile.title,
            "description": profile.description,
            "levels": [
                {
                    "id": level.id,
                    "num": level.num,
                    "level_name": level.level_name,
                    "last_version": level.versions[0].version,
                    "skills": [ls.skill for ls in level.versions[0].skills if ls.skill],
                }
                for level in profile.levels
            ],
        }
        return SProfile.model_validate(profile_dict)

    async def _validate_skills(self, levels: list[SLevelAdd]):
        skill_ids = set()
        for lvl in levels:
            skill_ids.update(lvl.skills)
        if skill_ids:
            skill_exists = await self.skill_repository.check_list(list(skill_ids))
            if len(skill_exists) != len(skill_ids):
                missing = [str(s) for s in skill_ids if s not in skill_exists]
                raise DataValidationError(f"Навыков с id = [{','.join(missing)}]")

    async def add_levels(self, profile_id: int, levels: list[SLevelAdd]):
        await self._validate_skills(levels)
        new_levels = []
        level_versions = []
        level_skills = []
        for lvl in levels:
            new_level = await self.level_repository.add(
                {"profile_id": profile_id, "level_name": lvl.level_name, "num": lvl.num}
            )
            new_levels.append(new_level)
            level_version = await self.level_version_repository.add(
                {"profile_level_id": new_level.id}
            )
            level_versions.append(level_version)
            for s in lvl.skills:
                level_skills.append(
                    {"profile_level_version_id": level_version.id, "skill_id": s}
                )

        await self.level_skill_repository.add_list(level_skills)

    async def add_profile(self, model: SProfileAdd):
        profile = await self.add(model.profile)

        if model.levels:
            await self.add_levels(profile.id, model.levels)

        return profile

    async def update_by_id(self, profile_id: int, profile: SProfileUpdate):
        profile_old: SProfile = await self.get_with_details(profile_id)


        res = await super().update_by_id(profile_id, profile.profile)

        if not profile.levels:
            return

        await self._validate_skills(profile.levels)
        exist_level_dict = {lvl.id: lvl for lvl in profile_old.levels}
        new_levels_ids = set()
        lvl_add = []
        lvl_upd = []
        for lvl in profile.levels:
            if lvl.id is None:
                lvl_add.append(lvl)
            else:
                new_levels_ids.add(lvl.id)
                if lvl.id in exist_level_dict:
                    lvl_upd.append(lvl)

        lvl_del = [
            lvl_id for lvl_id in exist_level_dict.keys() if lvl_id not in new_levels_ids
        ]
        if lvl_del:
            await self.level_repository.delete_list(lvl_del)

        if lvl_add:
            await self.add_levels(profile_id, lvl_add)

        if lvl_upd:
            level_skills = []
            for lvl in lvl_upd:
                old_level = exist_level_dict[lvl.id]
                if old_level.level_name != lvl.level_name:
                    await self.level_repository.update_by_id(lvl.id, {"level_name": lvl.level_name})
                old_skills = set(s.id for s in old_level.skills)
                new_skills = set(lvl.skills)
                if old_skills != new_skills:
                    new_version_num = old_level.last_version + 1
                    new_version = await self.level_version_repository.add(
                        {"profile_level_id": lvl.id, "version": new_version_num}
                    )
                    level_skills += [
                        {"profile_level_version_id": new_version.id, "skill_id": s}
                        for s in lvl.skills
                    ]
            if level_skills:
                await self.level_skill_repository.add_list(level_skills)


