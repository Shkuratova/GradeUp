from sqlalchemy import select, insert, update
from sqlalchemy.orm import contains_eager
from db.repository import BaseRepository
from db.models.skills import StageQuestion
from db.repository.decorators import db_exception_handler

class QuestionRepository(BaseRepository):
    model = StageQuestion

    @db_exception_handler
    async def get_all(self, filter_dict: dict):
        stmt = (
                 select(StageQuestion)
                .options(contains_eager(StageQuestion.stage))
                .filter_by(**filter_dict)
            )
        res = await  self._session.execute(stmt)
        return res.unique().scalars().all()

    @db_exception_handler
    async def get_questions_id(self, stage_id: int):
        stmt = select(self.model.id).where(self.model.stage_id == stage_id)
        res = await self._session.execute(stmt)
        return res.scalars().all()

