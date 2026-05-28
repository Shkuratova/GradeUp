from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    UserStageRepository,
    UserProfileRepository,
    StageRepository,
    UserSkillRepository,
    UserLevelRepository,
)
from exceptions.common import NotFoundException, DataValidationError
from schemas.evaluations import EvaluationSchema
from schemas.user_profile import UserStageAdd
from services.base import BaseService


class UserStageService(BaseService):
    entity_name = "Оценка этапа"
    unique_fields = ["user_skill_id", "stage_version_id"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = UserStageRepository(session)
        self.stage_repository = StageRepository(session)
        self.user_skill_repository = UserSkillRepository(session)
        self.user_level_repository = UserLevelRepository(session)
        self.user_profile_repository = UserProfileRepository(session)

    async def ensure_user_stage(self, user_id: int, stage_id: int):

        stage_version = await self.stage_repository.get_last_version(stage_id)

        if stage_version is None:
            raise NotFoundException(f"Этап подтверждения с id = {stage_id} не найден.")

        stage = stage_version.stage

        is_available = await self.user_profile_repository.has_available_stage(
            user_id,
            stage_id,
        )

        if not is_available:
            raise NotFoundException("Выбранный этап недоступен пользователю.")

        user_profile = await self.user_profile_repository.get_profile(user_id)
        if user_profile.current_level_id is None:
            raise NotFoundException("У пользователя отсутствует текущий уровень.")

        user_skill = await self.user_skill_repository.get_by_user(
            user_id,
            stage.skill_id,
        )

        if user_skill is None:
            user_skill = await self.user_skill_repository.add(
                {
                    "user_id": user_id,
                    "skill_id": stage.skill_id,
                }
            )

        stage_dict = {
            "user_skill_id": user_skill.id,
            "stage_version_id": stage_version.id,
        }

        user_stage = await self.repository.get_one_by_filter(stage_dict)

        if user_stage is not None:
            return user_stage
        else:
            user_stage = await self.repository.add(stage_dict)

        return user_stage

    async def evaluate(self, new_stage: UserStageAdd):
        user_stage = await self.ensure_user_stage(
            new_stage.user_id,
            new_stage.stage_id,
        )

        if user_stage.is_accepted:
            raise DataValidationError("Этап уже подтвержден.")

        stage_dict = new_stage.model_dump(
            exclude_none=True, exclude={"user_id", "stage_id"}
        )

        res = await self.repository.update_by_id(user_stage.id, stage_dict)

        stage = await self.stage_repository.get_by_id(new_stage.stage_id)
        accepted_cnt = await self.repository.accepted_count(
            stage.skill_id, user_stage.user_skill_id
        )
        total_cnt = await self.stage_repository.stage_count(stage.skill_id)
        if accepted_cnt >= total_cnt:
            await self.user_skill_repository.update_by_id(
                user_stage.user_skill_id, {"is_accepted": True}
            )

        return await self.get_evaluation(user_stage.id)

    async def get_evaluation(self, user_stage_id: int):
        evaluation =  await self.repository.get_evaluation(user_stage_id)
        if evaluation is None:
            raise NotFoundException(f"Оценка пользователя с id = {user_stage_id} не найдена.")
        return EvaluationSchema.model_validate(evaluation, from_attributes=True)
