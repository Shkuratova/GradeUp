from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import LevelRepository
from services.base import BaseService


class LevelService(BaseService):
    entity_name = "Уровень"
    unique_fields = ["profile_id", "level_name"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = LevelRepository(session)

    async def get_structure(self, profile_level_id: int):
        return await self.repository.get_level_structure(profile_level_id)