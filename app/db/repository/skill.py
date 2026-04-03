from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import select
from db.repository.base import BaseRepository
from db.models import Skill, SkillStage

class SkillRepository(BaseRepository):
    model = Skill

    async def get_stages(self, filter_dict: dict):


        stmt = (
            select(Skill)
            .join(Skill.stages, isouter=True)
            .options(
                contains_eager(Skill.stages)
            )
            .filter_by(**filter_dict)
        )
        res = await self._session.execute(stmt)
        return res.unique().scalars().all()

class StageRepository(BaseRepository):
    model = SkillStage

def skill_repository_factory(session):
    return SkillRepository(session)

def stage_repository_factory(session):
    return StageRepository(session)
