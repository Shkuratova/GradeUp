import sqlalchemy.ext.asyncio

from db.repository import (
    LevelSkillRepository,
    UserProfileRepository,
    UserLevelRepository,
    ProfileRepository,
    SkillRepository,
    LevelRepository,
)
from exceptions.common import (
    DataValidationError,
    NotFoundException,
    ConflictException,
)
from schemas.profiles import (
    SProfileAdd,
    ProfileDetail,
    SProfileUpdate,
    SLevelAdd,
    SLevelUpdate,
    LevelDetail,
    ProfileFilter,
    ProfileStructure,
)
from services.base import BaseService


class ProfileService(BaseService):

    entity_name = "Профиль"
    unique_fields = ["title"]

    def __init__(self, session: sqlalchemy.ext.asyncio.AsyncSession):
        super().__init__(session)
        self.repository = ProfileRepository(session)
        self.level_repository = LevelRepository(session)
        self.level_skill_repository = LevelSkillRepository(session)
        self.skill_repository = SkillRepository(session)
        self.user_profile_repository = UserProfileRepository(session)
        self.user_level_repository = UserLevelRepository(session)

    async def get_profile_list(self, filters: ProfileFilter):
        filter_dict = filters.model_dump(exclude_none=True)
        profiles = await self.repository.get_list(filter_dict=filter_dict)
        return profiles

    async def get_profile_levels(self, filters: ProfileFilter):

        profiles = await self.repository.get_profiles_with_levels(
            departments_id=filters.departments_id
        )
        return [ProfileDetail.model_validate(p) for p in profiles]

    async def get_with_details(self, profile_id: int):
        profile = await self.repository.get_profiles_with_levels(profile_id)
        if profile is None:
            raise NotFoundException(f"Профиль с id = {profile_id} не найден.")
        return ProfileDetail.model_validate(profile)

    async def _validate_skills(self, levels: list[SLevelAdd]):
        skill_ids = set()
        for lvl in levels:
            if lvl.skills:
                skill_ids.update(lvl.skills)
                skill_exists = await self.skill_repository.check_list(list(skill_ids))
                if len(skill_exists) != len(skill_ids):
                    missing = [str(s) for s in skill_ids if s not in skill_exists]
                    raise DataValidationError(f"Навыков с id = [{','.join(missing)}]")

    async def add_levels(self, profile_id: int, levels: list[SLevelAdd]):
        await self._validate_skills(levels)
        new_levels = []
        level_skills = []
        for lvl in levels:
            new_level = await self.level_repository.add(
                {"profile_id": profile_id, "level_name": lvl.level_name, "num": lvl.num}
            )
            new_levels.append(new_level)
            if lvl.skills:
                for s in lvl.skills:
                    level_skills.append(
                        {"profile_level_id": new_level.id, "skill_id": s}
                    )

        if level_skills:
            await self.level_skill_repository.add_list(level_skills)

    async def add_profile(self, model: SProfileAdd):
        profile = await self.add(model.profile)

        if model.levels:
            await self.add_levels(profile.id, model.levels)

        return await self.get_with_details(profile.id)

    @staticmethod
    def _level_skills_equal(new_level: SLevelUpdate, old_level: LevelDetail):
        old_skills = set(s.id for s in old_level.skills)
        return set(new_level.skills) == old_skills

    async def update_by_id(self, profile_id: int, profile: SProfileUpdate):
        profile_old: ProfileDetail = await self.get_with_details(profile_id)
        res = await super().update_by_id(profile_id, profile.profile)

        await self._validate_skills(profile.levels)

        old_levels = {lvl.id: lvl for lvl in profile_old.levels}
        upd_levels = {lvl.id: lvl for lvl in profile.levels if lvl.id in old_levels}

        if del_levels := set(old_levels.keys()) - set(upd_levels.keys()):
            user_cnt = await self.user_level_repository.get_level_count(
                list(del_levels)
            )
            if user_cnt:
                raise ConflictException(
                    "Нельзя удалить уровень, по которому есть прогресс пользователя."
                )
            await self.level_repository.delete_list(list(del_levels))

        if add_levels := [lvl for lvl in profile.levels if lvl.id is None]:
            await self.add_levels(profile_id, add_levels)

        if upd_levels:
            level_skills = []
            for lvl in upd_levels.values():
                old_level = old_levels[lvl.id]
                if old_level.level_name != lvl.level_name or old_level.num != lvl.num:
                    await self.level_repository.update_by_id(
                        lvl.id, {"level_name": lvl.level_name, "num": lvl.num}
                    )
                if lvl.skills:
                    old_skills = set(s.id for s in old_level.skills)
                    new_skills = set(lvl.skills)
                    if add_skill := new_skills - old_skills:
                        level_skills += [
                            {"profile_level_id": lvl.id, "skill_id": s}
                            for s in add_skill
                        ]
                    if del_skill := old_skills - new_skills:
                        await self.level_skill_repository.delete_by_skill_ids(
                            lvl.id, list(del_skill)
                        )
            if level_skills:
                await self.level_skill_repository.add_list(level_skills)
        return await self.get_with_details(profile_id)

    async def get_structure(self, profile_id):
        res = await self.repository.get_profile_structure_by_id(profile_id)
        return ProfileStructure.model_validate(res, from_attributes=True)

    async def delete(self, profile_id):
        user_profile_cnt = await self.user_profile_repository.get_count(profile_id)
        if user_profile_cnt:
            raise ConflictException(
                f"Нельзя удалить профиль, который назначен пользователю (Пользователей с выбранным профилем: {profile_id})"
            )
        return await self.repository.delete_by_id(profile_id)
