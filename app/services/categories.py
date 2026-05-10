from sqlalchemy.ext.asyncio import AsyncSession
from services.base import BaseService
from db.repository import CategoryRepository, SkillCategoryRepository


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
