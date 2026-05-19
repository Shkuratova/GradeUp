from services.base import BaseService


class LevelService(BaseService):
    entity_name = "Уровень"
    unique_fields = ["profile_id", "level_name"]
