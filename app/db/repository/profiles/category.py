from sqlalchemy import delete

from db.models import Category, SkillCategory
from db.repository.base import BaseRepository
from db.repository.decorators import db_exception_handler


class CategoryRepository(BaseRepository):
    model = Category


class SkillCategoryRepository(BaseRepository):
    model = SkillCategory

    @db_exception_handler
    async def delete_categories(self, skill_id: int, data_ids: list[int]):
        stmt = delete(SkillCategory).where(
            SkillCategory.skill_id == skill_id, SkillCategory.category_id.in_(data_ids)
        )
        res = await self._session.execute(stmt)
        return res
