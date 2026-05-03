from sqlalchemy.ext.asyncio import AsyncSession

from services.base import BaseService
from db.repository.skill import (
    SkillRepository,
    StageRepository,
    CategoryRepository,
    LevelSkillRepository,
    SkillCategoryRepository,
)
from pydantic import BaseModel
from schemas.skills import SSkillAdd, StageAdd, SkillFilter
from schemas.categories import SkillCategory

class SkillService(BaseService):

    entity_name = "Навык"
    unique_fields = ["title"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = SkillRepository(session)


    async def get_all_by_categories(self, filter_model: SkillFilter):
        if filter_model.categories:
            res = await self.repository.get_all_by_categories(filter_model.categories)
        else:
            res = await self.get_all()
        return res

    async def get_skills_stages(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_none=True)
        res = await self.repository.get_stages(filter_dict)
        return res

    async def add_skill(self, model: SSkillAdd):
        skill = await self.repository.add(model.skill.model_dump(exclude_none=True))

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

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = StageRepository(session)


class LevelSkillService(BaseService):
    unique_fields = ["skill_id", "profile_level_id"]


    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = LevelSkillRepository(session)

class CategoryService(BaseService):
    entity_name = "Категория"
    unique_fields = ["category_name"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = CategoryRepository(session)

class SkillCategoryService(BaseService):
    unique_fields = ["skill_id", "category_id"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = SkillCategoryRepository(session)
