from sqlalchemy.ext.asyncio import AsyncSession

from db.models.types import DepartmentRole
from db.repository import (
    UserProfileRepository,
    LevelRepository,
    UserLevelRepository,
    UserSkillRepository, DepartmentProfileRepository,
)
from exceptions.common import (
    NotFoundException,
    DataValidationError,
    AlreadyExistException,
    ConflictException,
)
from schemas.profiles import ProfileList
from schemas.user_profile import (
    UserProfileAdd,
    ProfileAvailableSkills,
    UserProfileSchema,
    UserProfileFilter,
    GradeUpResult,
    Level,
)
from schemas.users import UserSchema, UserInfo
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
        self.department_profile_repository = DepartmentProfileRepository(session)


    async def get_profile(self, user_id: int):
        profile = await self.repository.get_one_by_filter({"user_id": user_id})
        if profile is None:
            raise NotFoundException(f"Сотруднику с id = {user_id} не назначен профиль.")
        return profile

    async def get_all_with_progress(self, filters: UserProfileFilter):
        user_profiles = await self.repository.get_all_with_progress(
            filters.model_dump(exclude_none=True, exclude={"only_subordinates"})
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

    async def create(self, model: UserProfileAdd, current_user: UserInfo):
        profile = await ProfileService(self.session).get_by_id(model.profile_id)
        user = await UserService(self.session).get_user_info(model.user_id)
        if current_user.is_division_supervisor() or current_user.is_admin():
            in_user_department = await self.department_profile_repository.get_one_by_filter({"department_id": user.department_id, "profile_id": model.profile_id})
            if user.is_department_supervisor() and in_user_department is not None:
                raise ConflictException("Руководителю отдела нельзя назначить профиль, доступный в его отделе")
            elif user.department_role == DepartmentRole.EMPLOYEE and in_user_department is None:
                raise ConflictException("Нельзя назначить сотруднику профиль, недоступный в его отделе")

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

    async def get_available_skills(self, user_id):
        skills = await self.repository.get_available_skills(user_id)
        if skills is None:
            raise NotFoundException(f"Нет доступных навыков для назначения встречи пользователю (user_id={user_id}).")
        return ProfileAvailableSkills.model_validate(skills, from_attributes=True)

    async def gradeup(self, user_id: int):
        user_profile = await self.user_level_repository.get_current_lvl(user_id)
        user_level = await self.user_level_repository.get_one_by_filter(
            {"profile_level_id": user_profile.current_level_id, "user_id": user_id}
        )
        if not user_profile or not user_level:
            raise NotFoundException(
                f"Не найден профиль пользователя с user_id={user_id}"
            )

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
