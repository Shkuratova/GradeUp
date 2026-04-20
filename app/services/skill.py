from services.base import BaseService
from db.repository.skill import (
    SkillRepository,
    StageRepository,
    LevelSkillRepository,
)
from pydantic import BaseModel
from schemas.skills import SSkillAdd, StageAdd
from db.uow import unit_of_work


class SkillService(BaseService):

    entity_name = "Навык"
    unique_fields = ["title"]
    repository_factory = SkillRepository

    async def get_skills_stages(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            repository: SkillRepository = self.repository_factory(uow.session)
            res = await repository.get_stages(filter_dict)
        return res

    async def add_skill(self, model: SSkillAdd):
        repository = SkillRepository(self.session)
        skill = await repository.add(model.skill.model_dump(exclude_none=True))

        if not model.stages:
            return skill

        stage_repository = StageRepository(self.session)
        stages = [
            {"skill_id": skill.id, "confirmation_type": ct} for ct in model.stages
        ]
        await stage_repository.add_list(stages)
        return skill


class StageService(BaseService):
    entity_name = "Этап подтверждения"
    repository_factory = StageRepository
    # unique_fields = []


class LevelSkillService(BaseService):
    unique_fields = ["skill_id", "profile_level_id"]
    repository_factory = LevelSkillRepository
