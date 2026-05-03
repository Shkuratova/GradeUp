from services.base import BaseService
from schemas.profiles import SLevelAdd, SLevelUpdate, SLevel


class LevelService(BaseService):
    entity_name = "Уровень"

    async def process_levels(
        self, profile_id: int, levels: list, old_levels: dict = None
    ):
        pass

    async def add_levels_with_skills(self, profile_id: int, levels: list[SLevelAdd]):
        pass

    async def update_levels_with_skills(
        self, profile_id: int, old_levels: list[SLevel], levels: list[SLevelUpdate]
    ):
        await self.process_levels(profile_id, levels, {l.id: l for l in old_levels})
