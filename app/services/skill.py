from services.base import BaseService
from db.repository.skill import skill_repository_factory


class SkillService(BaseService):

    entity_name = "Навык"
    unique_field = "title"


skill_service = SkillService(repository_factory=skill_repository_factory)

