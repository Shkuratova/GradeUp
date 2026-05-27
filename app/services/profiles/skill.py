from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import (
    SkillRepository,
    SkillCategoryRepository,
    UserSkillRepository,
    LevelRepository,
)
from exceptions.common import NotFoundException, ConflictException
from schemas.skills import (
    SkillFilter,
    SkillDetail,
    SkillUpdateForm,
    SkillAddForm,
)
from services.base import BaseService
from services.profiles.stage import StageService


class SkillService(BaseService):

    entity_name = "Навык"
    unique_fields = ["title"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = SkillRepository(session)
        self.skill_category_repository = SkillCategoryRepository(session)
        self.user_skill_repository = UserSkillRepository(session)
        self.level_repository = LevelRepository(session)

    async def get_list(self, filter_model: SkillFilter):
        res = await self.repository.get_list_by_categories(filter_model.categories)
        return res

    async def get_all_by_categories(self, filter_model: SkillFilter):
        res = await self.repository.get_all_by_categories(filter_model.categories)
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

        old_categories = old_skill.categories
        new_cat_ids = set(model.categories)
        old_cat_ids = set(cat.id for cat in old_categories)
        if del_cat_id := old_cat_ids - new_cat_ids:
            await self.skill_category_repository.delete_categories(
                skill_id, list(del_cat_id)
            )
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

    async def delete(self, skill_id):
        user_count = await self.user_skill_repository.get_count_by_skill(skill_id)
        if user_count:
            raise ConflictException(
                f"Нельзя удалить навык, по которому есть прогресс у пользователя (Пользователей, имеющих прогресс по навыку {user_count})."
            )
        profile_count = await self.level_repository.get_profile_count_by_skill(skill_id)
        if profile_count:
            raise ConflictException(
                f"Нельзя удалить навык, который используется в профиле (Профилей, содержащих выбранный навык {profile_count})"
            )
        await self.delete_by_id(skill_id)
