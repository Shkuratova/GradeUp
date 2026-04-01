from db.repository.base import BaseRepository
from db.models import Skill, SkillStage

class SkillRepository(BaseRepository):
    model = Skill

class SkillStageRepository(BaseRepository):
    model = SkillStage

def skill_repository_factory(session):
    return SkillRepository(session)