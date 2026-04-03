from services.base import BaseService
from db.repository.skill import skill_repository_factory, stage_repository_factory, SkillRepository, StageRepository
from pydantic import BaseModel
from db.uow import unit_of_work

class SkillService(BaseService):

    entity_name = "Навык"
    unique_field = "title"

    async def get_skills_stages(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            repository: SkillRepository = self.repository_factory(uow.session)
            res = await repository.get_stages(filter_dict)
        return res

class StageService(BaseService):
    entity_name = "Этап подтверждения"
    #unique_fields = []

skill_service = SkillService(repository_factory=skill_repository_factory)
stage_service = StageService(repository_factory=stage_repository_factory)

