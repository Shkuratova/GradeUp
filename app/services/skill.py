from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from db.repository import QuestionRepository
from db.repository import (
    SkillRepository,
    CategoryRepository,
    LevelSkillRepository,
    SkillCategoryRepository,
    StageVersionRepository,
    StageRepository,
)
from exceptions.common import NotFoundException, DataValidationError
from schemas.skills import (
    SkillFilter,
    SkillDetail,
    SkillUpdateForm,
    SkillAddForm,
)
from services.base import BaseService
from services.stages import StageService


class SkillService(BaseService):

    entity_name = "Навык"
    unique_fields = ["title"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = SkillRepository(session)
        self.skill_category_repository = SkillCategoryRepository(session)

    async def get_all_by_categories(self, filter_model: SkillFilter):
        res = await self.repository.get_all_by_categories(filter_model.categories)
        return res

    async def get_skills_stages(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_none=True)
        res = await self.repository.get_stages(filter_dict)
        return res

    async def get_skill_with_questions(self, skill_id: int):
        skill = await self.repository.get_last_skill_with_questions(skill_id)
        if skill is None:
            raise NotFoundException(f"Навык с id = {skill_id} не найден.")
        return SkillDetail.model_validate(skill)

    async def add_skill(self, model: SkillAddForm):
        new_skill = await self.add(model.skill)

        if model.categories:
            categories = set(model.categories)
            await self.skill_category_repository.add_list(
                [
                    {"skill_id": new_skill.id, "category_id": cat_id}
                    for cat_id in categories
                ]
            )

        if not model.stages:
            return new_skill

        await StageService(self.session).add_stages(new_skill.id, model.stages)
        return await self.get_skill_with_questions(new_skill.id)

    async def update(self, skill_id: int, model: SkillUpdateForm):
        old_skill: SkillDetail = await self.get_skill_with_questions(skill_id)

        res = await self.update_by_id(skill_id, model.skill)

        old_categories =old_skill.categories
        new_cat_ids = set(model.categories)
        old_cat_ids = set(cat.id for cat in old_categories)
        if del_cat_id := old_cat_ids - new_cat_ids:
            await self.skill_category_repository.delete_categories(skill_id, list(del_cat_id))
        if add_cat_ids := new_cat_ids - old_cat_ids:
            await self.skill_category_repository.add_list(
                [
                    {"skill_id": skill_id, "category_id": cat_id}
                    for cat_id in add_cat_ids
                ]
            )
        if model.stages:
            await StageService(self.session).update_stages(
                skill_id, old_skill.stages, model.stages
            )

        return await self.get_skill_with_questions(skill_id)

    async def get_accessible_skills(self, current_user):
        pass


class LevelSkillService(BaseService):
    unique_fields = ["skill_id", "profile_level_id"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = LevelSkillRepository(session)
