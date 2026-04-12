from services.base import BaseService
from db.repository.skill import (
    skill_repository_factory,
    stage_repository_factory,
    SkillRepository,
    StageRepository,
    level_skill_repository_factory,
    LevelSkillRepository,
)
from pydantic import BaseModel
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

class StageService(BaseService):
    entity_name = "Этап подтверждения"
    repository_factory = StageRepository
    #unique_fields = []


class LevelSkillService(BaseService):
    unique_fields = ["skill_id", "profile_level_id"]
    repository_factory = LevelSkillRepository


skill_service = SkillService()
stage_service = StageService()
level_skill_service = LevelSkillService()
