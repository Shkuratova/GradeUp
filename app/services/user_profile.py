from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    UserProfileRepository,
    LevelRepository,
    UserLevelRepository,
    UserSkillRepository,
)
from exceptions.common import NotFoundException
from schemas.user_profile import (
    UserProfileAdd,
    ProfileAvailableSkills,
    UserProfileTitle,
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

    async def _add_user_level(self, user_id: int, profile_id: int ):
        current_lvl = await self.level_repository.get_last_level_by_num(
            profile_id=profile_id, level_num=1
        )
        if current_lvl is None:
            raise NotFoundException("Нет доступного уровня внутри профиля.")

        user_level = await self.user_level_repository.add(
            {"user_id": user_id, "profile_level_id": current_lvl.id}
        )

    async def create(self, model: UserProfileAdd):
        profile = await ProfileService(self.session).get_by_id(model.profile_id)
        user = await UserService(self.session).get_by_id(model.user_id)
        current_lvl = await self.level_repository.get_last_level_by_num(profile_id=model.profile_id, level_num=1)
        if current_lvl is None:
            raise NotFoundException("Нет доступного уровня внутри профиля.")

        data_dict = model.model_dump()

        user_profile = await self.repository.add({**data_dict, 'current_level_id': current_lvl})
        user_level = await self.user_level_repository.add({
            'user_id': model.user_id,
            'profile_level_id': current_lvl
        })
        return user_profile

    async def update(self):
        pass

    async def delete(self):
        pass

    async def status(self, user_profile_id: int):
        user_profile = await self.repository.get_profile(user_profile_id)
        if user_profile is None:
            raise NotFoundException(f"Профиль пользователя с id = {user_profile_id} не найден.")
        user_profile_model = UserProfileTitle.model_validate(user_profile)

        user_progress = await self.repository.get_progress(user_profile.user_id, user_profile.profile_id)
        profile_levels = {}

        for row in user_progress:
            level_id = row["profile_level_id"]

            if level_id not in profile_levels:
                profile_levels[level_id] = {
                    "profile_level_id": level_id,
                    "is_closed": row["is_closed"],
                    "skills": {},
                }

            skills = profile_levels[level_id]["skills"]

            skill_id = row["skill_id"]

            if skill_id not in skills:
                skills[skill_id] = {
                    "skill_id": skill_id,
                    "skill_title": row["skill_title"],
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
            ]
        }

        return response

    async def get_available_skills(self, user_id):
        skills =  await self.repository.get_available_skills(user_id)
        return ProfileAvailableSkills.model_validate(skills)

    async def gradeup(self, user_profile_id):
        pass
