from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    UserProfileRepository,
    LevelRepository,
    UserLevelRepository,
    UserSkillRepository,
)
from exceptions.common import NotFoundException, DataValidationError
from schemas.user_profile import (
    UserProfileAdd,
    ProfileAvailableSkills,
    UserProfileTitle,
    UserProfileProgress,
)
from services import BaseService, UserService, ProfileService


class UserProfileService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = UserProfileRepository(self.session)
        self.level_repository = LevelRepository(self.session)
        self.user_level_repository = UserLevelRepository(self.session)
        self.user_skill_repository = UserSkillRepository(session)

    async def get_all_with_progress(self):
        user_profiles = await self.repository.get_all_with_progress()
        return user_profiles

    async def _add_user_level(self, user_id: int, profile_id: int, level_num: int = 1):
        current_lvl_id = await self.level_repository.get_last_level_by_num(
            profile_id=profile_id, level_num=level_num
        )
        if current_lvl_id is None:
            raise NotFoundException("Нет доступного уровня внутри профиля.")

        user_level = await self.user_level_repository.add(
            {"user_id": user_id, "profile_level_id": current_lvl_id}
        )
        return user_level

    async def create(self, model: UserProfileAdd):
        profile = await ProfileService(self.session).get_by_id(model.profile_id)
        user = await UserService(self.session).get_by_id(model.user_id)
        current_lvl = await self.level_repository.get_last_level_by_num(
            profile_id=model.profile_id, level_num=1
        )
        if current_lvl is None:
            raise NotFoundException("Нет доступного уровня внутри профиля.")

        data_dict = model.model_dump()

        user_profile = await self.repository.add(
            {**data_dict, "current_level_id": current_lvl}
        )
        user_level = await self.user_level_repository.add(
            {"user_id": model.user_id, "profile_level_id": current_lvl}
        )
        return user_profile

    async def update(self):
        pass

    async def delete(self):
        pass

    async def status(self, user_profile_id: int):
        user_profile = await self.repository.get_profile(user_profile_id)
        if user_profile is None:
            raise NotFoundException(
                f"Профиль пользователя с id = {user_profile_id} не найден."
            )
        user_profile_model = UserProfileTitle.model_validate(user_profile)

        user_progress = await self.repository.get_progress(
            user_profile.user_id, user_profile.profile_id
        )
        profile_levels = {}

        for row in user_progress:
            level_id = row["profile_level_id"]

            if level_id not in profile_levels:
                profile_levels[level_id] = {
                    "profile_level_id": level_id,
                    "user_level_id": row["user_level_id"],
                    "num": row["num"],
                    "level_name": row["level_name"],
                    "is_closed": row["is_closed"],
                    "skills": {},
                }

            skills = profile_levels[level_id]["skills"]

            skill_id = row["skill_id"]

            if skill_id not in skills:
                skills[skill_id] = {
                    "skill_id": skill_id,
                    "title": row["skill_title"],
                    "stages": [],
                }

            skills[skill_id]["stages"].append(
                {
                    "stage_id": row["stage_id"],
                    "confirmation_type": row["confirmation_type"],
                    "stage_accepted": row["stage_accepted"],
                }
            )

        response = {
            **user_profile_model.model_dump(),
            "profile_levels": [
                {**level, "skills": list(level["skills"].values())}
                for level in profile_levels.values()
            ],
        }

        return UserProfileProgress(**response)

    async def get_skill_progress(self, user_id: int, skill_id: int):
        skill_detail = await self.user_skill_repository.get_skill_detail(
            user_id, skill_id
        )

        if not skill_detail:
            return None

        skill_data = {
            "id": skill_detail[0]["skill_id"],
            "title": skill_detail[0]["title"],
            "description": skill_detail[0]["description"],
            "literature": skill_detail[0]["literature"],
            "stages": [],
        }

        stages_map = {}

        for row in skill_detail:
            stage_id = row["stage_id"]

            if stage_id not in stages_map:
                stages_map[stage_id] = {
                    "id": stage_id,
                    "confirmation_type": row["confirmation_type"],
                }

            if row["user_stage_id"] is not None:
                stages_map[stage_id]["user_stage_id"] = row["user_stage_id"]
                stages_map[stage_id]["is_accepted"] = row["is_accepted"]
                stages_map[stage_id]["comment"] = row["comment"]
                stages_map[stage_id]["updated_at"] = row["updated_at"]
            else:
                stages_map[stage_id]["user_stage_id"] = None

        skill_data["stages"] = list(stages_map.values())

        return skill_data

    async def get_available_skills(self, user_id):
        skills = await self.repository.get_available_skills(user_id)
        return ProfileAvailableSkills.model_validate(skills, from_attributes=True)

    async def gradeup(self, user_profile_id):
        user_profile = await self.get_by_id(user_profile_id)
        current_level = await self.user_level_repository.get_current_lvl(user_profile.user_id, user_profile.current_level_id)
        print("CURRENT_LEVEL", current_level)
        accepted_skills = await self.user_skill_repository.get_accepted_count(current_level.id)
        total_skills = await self.level_repository.get_skills_cnt(current_level.profile_level_id)
        if accepted_skills != total_skills:
            raise DataValidationError("Для получения повышения сотрудник должен получить зачеты по всем навыкам.")

        await self.user_level_repository.update_by_id(current_level.id, {'is_closed': True})
        next_lvl = await self._add_user_level(user_profile.user_id, user_profile.profile_id, current_level.profile_level.num + 1)
        await self.repository.update_by_id(user_profile_id, {'current_level_id': next_lvl.profile_level_id})
        return await self.get_by_id(user_profile_id)



