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
    SProfileAdd,
    ProfileDetail,
    SProfileUpdate,
    SLevelAdd,
    SLevelUpdate, LevelDetail, ProfileFilter, ProfileList,
)
from schemas.users import UserInfo
from services.base import BaseService
from utils.roles import UserRole

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

    async def get_profile_list(self, filters: ProfileFilter, current_user: UserInfo):
        department_id = None

        if current_user.role_name == UserRole.SUPERVISOR:
            department_id = current_user.department_id
            if filters.department_id:
                filters.department_id = department_id

        filter_dict = filters.model_dump(exclude_none=True)
        profiles =  await self.repository.get_list(
            filter_dict=filter_dict,
            department_id=department_id,
        )
        return profiles

    async def get_profile_levels(self):
        profiles = await self.repository.get_profiles_with_latest_levels()
        print(profiles[0].__dict__)
        return [ProfileDetail.model_validate(profile) for profile in profiles]

    async def get_all_by_department_id(self, department_id: int):
        profiles = await self.repository.get_profiles_by_department(department_id)
        return profiles

    async def get_with_details(self, profile_id: int, current_user: UserInfo):

        department_id  = None
        if current_user.role_name == UserRole.SUPERVISOR:
            department_id = current_user.department_id

        profile = await self.repository.get_profiles_with_latest_levels(profile_id, department_id)

        if profile is None:
            raise NotFoundException(
                f"{self.entity_name} c id = {profile_id} не найден."
            )
        return ProfileDetail.model_validate(profile)

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

    @staticmethod
    def _level_skills_equal(new_level: SLevelUpdate, old_level: LevelDetail):
        old_skills = set(s.id for s in old_level.skills)
        return set(new_level.skills) == old_skills

    async def update_by_id(self, profile_id: int, profile: SProfileUpdate):
        profile_old: ProfileDetail = await self.get_with_details(profile_id)
        res = await super().update_by_id(profile_id, profile.profile)

        if not profile.levels:
            return

        await self._validate_skills(profile.levels)

        old_levels = {lvl.id: lvl for lvl in profile_old.levels}
        upd_levels = {lvl.id: lvl for lvl in profile.levels if lvl.id in old_levels}

        if del_levels := set(old_levels.keys()) - set(upd_levels.keys()):
            await self.level_repository.soft_delete_list(list(del_levels))

        if add_levels := [lvl for lvl in profile.levels if lvl.id is None]:
            await self.add_levels(profile_id, add_levels)

        if upd_levels:
            level_skills = []
            for lvl in upd_levels.values():
                old_level = old_levels[lvl.id]
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
