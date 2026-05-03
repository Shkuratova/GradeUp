from sqlalchemy.ext.asyncio import AsyncSession

from services.base import BaseService
from pydantic import BaseModel
from db.repository.skill import QuestionRepository
from db.uow import unit_of_work
from schemas.questions import QuestionAdd, QuestionUpdate
from exceptions.common import DataValidationError


class QuestionService(BaseService):
    entity_name = "Вопрос"
    unique_fields = ["num", "stage_id"]


    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = QuestionRepository(session)


    async def get_all(self, filter_model: BaseModel | None = None):
        filter_dict = filter_model.model_dump(exclude_none=True)
        return await self.repository.get_all(filter_dict)

    async def add(self, questions: list[QuestionAdd]):
        values_dict = [q.model_dump(exclude_none=True) for q in questions]
        await self.repository.add_list(values_dict)


