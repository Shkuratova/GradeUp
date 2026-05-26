from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    UserProfileRepository,
    LevelRepository,
    UserLevelRepository,
    UserSkillRepository,
)
from exceptions.common import (
    NotFoundException,
    DataValidationError,
    AlreadyExistException,
)
from schemas.profiles import ProfileList
from schemas.user_profile import (
    UserProfileAdd,
    ProfileAvailableSkills,
    UserProfileProgress,
    UserProfileSchema,
    UserProfileFilter,
    GradeUpResult,
    Level,
)
from schemas.user_progress import UserProfileProgress
from schemas.users import  UserSchema
from services.base import BaseService
from services.users.user import UserService
from services.profiles import ProfileService


class UserProfileService(BaseService):

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = UserProfileRepository(self.session)
        self.level_repository = LevelRepository(self.session)
        self.user_level_repository = UserLevelRepository(self.session)
        self.user_skill_repository = UserSkillRepository(session)

    async def get_profile(self, user_id: int):
        profile = await self.repository.get_one_by_filter({"user_id": user_id})
        if profile is None:
            raise NotFoundException(f"Сотруднику с id = {user_id} не назначен профиль.")
        return profile

    async def get_all_with_progress(self, filters: UserProfileFilter):
        user_profiles = await self.repository.get_all_with_progress(
            filters.model_dump(exclude_none=True)
        )
        return user_profiles

    async def _add_user_level(self, user_id: int, profile_id: int, level_num: int = 1):
        current_lvl = await self.level_repository.get_last_level_by_num(
            profile_id=profile_id, level_num=level_num
        )
        if current_lvl is None:
            raise NotFoundException("Нет доступного уровня внутри профиля.")

        user_level = await self.user_level_repository.add(
            {"user_id": user_id, "profile_level_id": current_lvl.id}
        )
        return current_lvl

    async def create(self, model: UserProfileAdd):
        profile = await ProfileService(self.session).get_by_id(model.profile_id)
        user = await UserService(self.session).get_by_id(model.user_id)
        if await self.repository.get_profile(model.user_id) is not None:
            raise AlreadyExistException("Пользователю уже назначен профиль.")
        current_lvl = await self.level_repository.get_last_level_by_num(
            profile_id=model.profile_id, level_num=1
        )
        if current_lvl is None:
            raise NotFoundException("Нет доступного уровня внутри профиля.")

        data_dict = model.model_dump()

        user_profile = await self.repository.add(
            {**data_dict, "current_level_id": current_lvl.id}
        )
        user_level = await self.user_level_repository.get_by_level_id(
            model.user_id, current_lvl.id
        )
        if user_level is None:
            user_level = await self.user_level_repository.add(
                {"user_id": model.user_id, "profile_level_id": current_lvl.id}
            )
        return UserProfileSchema(
            id=user_profile.id,
            user=UserSchema.model_validate(user, from_attributes=True),
            profile=ProfileList.model_validate(profile, from_attributes=True),
        )

    async def get_skill_questions(self, user_id: int, skill_id: int, questions: bool = False):
        skill_detail = await self.user_skill_repository.get_skill_detail_questions(
            user_id, skill_id
        )

        if not skill_detail:
            return None

        first = skill_detail[0]

        skill_data = {
            "id": first["skill_id"],
            "title": first["title"],
            "description": first["description"],
            "literature": first["literature"],
            "stages": [],
        }

        stages_map = {}

        for row in skill_detail:
            stage_id = row["stage_id"]

            if stage_id not in stages_map:
                stages_map[stage_id] = {
                    "id": stage_id,
                    "confirmation_type": row["confirmation_type"],
                    "user_stage_id": row["user_stage_id"],
                    "is_accepted": row["is_accepted"],
                    "comment": row["comment"],
                    "updated_at": row["updated_at"],
                    "questions": [],
                }

            stage = stages_map[stage_id]

            if row["num"] is not None and questions:
                stage["questions"].append(
                    {
                        "num": row["num"],
                        "question": row["question"],
                        "answer": row["answer"],
                    }
                )

        skill_data["stages"] = list(stages_map.values())

        return skill_data


    async def get_available_skills(self, user_id):
        skills = await self.repository.get_available_skills(user_id)
        return ProfileAvailableSkills.model_validate(skills, from_attributes=True)

    async def gradeup(self, user_id: int):
        user_profile = await self.user_level_repository.get_current_lvl(user_id)
        user_level = await self.user_level_repository.get_one_by_filter(
            {"profile_level_id": user_profile.current_level_id, "user_id": user_id}
        )
        if not user_profile or not user_level:
            raise NotFoundException(f"Не найден профиль пользователя с user_id={user_id}")

        accepted_skills = await self.user_skill_repository.get_accepted_count(
            user_id, user_profile.current_level.id
        )
        total_skills = await self.level_repository.get_skills_cnt(
            user_profile.current_level.id
        )
        if accepted_skills != total_skills:
            raise DataValidationError(
                "Для получения повышения сотрудник должен получить зачеты по всем навыкам."
            )

        await self.user_level_repository.update_by_id(
            user_level.id, {"is_closed": True}
        )
        next_lvl = await self._add_user_level(
            user_profile.user_id,
            user_profile.profile_id,
            user_profile.current_level.num + 1,
        )
        old_level = user_profile.current_level.level_name

        await self.repository.update_by_id(
            user_profile.id, {"current_level_id": next_lvl.id}
        )
        res = GradeUpResult(
            profile_id=user_profile.profile_id,
            old_level=Level.model_validate(user_profile.current_level, from_attributes=True),
            new_level=Level.model_validate(next_lvl, from_attributes=True)
        )
        return res

    async def delete(self, user_id: int):
        await self.user_level_repository.delete_by_user(user_id)
        await self.repository.delete_by_user_id(user_id)

    async def progress(self, user_id):
        res = await self.repository.get_profile_progress(user_id)
        return UserProfileProgress.model_validate(res, from_attributes=True)
