from services.base import BaseService
from pydantic import BaseModel
from db.repository.questions import QuestionRepository
from db.uow import unit_of_work
from schemas.questions import QuestionAdd, QuestionUpdate
from exceptions.common import DataValidationError


class QuestionService(BaseService):
    entity_name = "Вопрос"
    unique_fields = ["num", "stage_id"]
    repository_factory = QuestionRepository
    async def get_all(self, filter_model: BaseModel | None = None):
        filter_dict = filter_model.model_dump(exclude_none=True)
        async with unit_of_work() as uow:
            repository: QuestionRepository = self.repository_factory(uow.session)
            return await repository.get_all(filter_dict)

    async def add(self, questions: list[QuestionAdd]):
        async with unit_of_work() as uow:
            repository: QuestionRepository = self.repository_factory(uow.session)
            values_dict = [q.model_dump(exclude_none=True) for q in questions]
            await repository.add_list(values_dict)

    async def update(self, questions: list[QuestionUpdate]):
        if not questions:
            raise DataValidationError("Хотя бы один вопрос должен быть передан")

        async with unit_of_work() as uow:
            repository: QuestionRepository = self.repository_factory(uow.session)

            stage_id = questions[0].stage_id

            existing_nums = await repository.get_questions_id(stage_id)

            q_upd = [q for q in questions if q.num in existing_nums]
            q_add = [q for q in questions if q.num not in existing_nums]

            for q in q_upd:
                 await repository.update_by_id(q.id, q.model_dump(exclude_none=True))

            if q_add:
                await repository.add_list(
                    [q.model_dump(exclude_none=True) for q in q_add]
                )
            return len(q_upd), len(q_add)

