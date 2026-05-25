from sqlalchemy.ext.asyncio import AsyncSession
from services import BaseService
from db.repository import StageRepository, StageVersionRepository, QuestionRepository
from schemas.skills import (
    StageQuestionsSchema,
    StageAdd,
    StageUpdate,
    StageAddDB,
    QuestionAdd,
    Question,
)
from exceptions.common import DataValidationError, NotFoundException


class StageService(BaseService):
    entity_name = "Этап подтверждения"
    repository_factory = StageRepository
    unique_fields = ["skill_id", "confirmation_type"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = StageRepository(session)
        self.stage_version_repository = StageVersionRepository(session)
        self.question_repository = QuestionRepository(session)

    @staticmethod
    def _questions_lists_equal(
        new_questions: list[QuestionAdd] | None,
        old_questions: list[Question] | None,
    ) -> bool:

        if new_questions is None or old_questions is None:
            return new_questions == old_questions

        normalize = lambda questions: sorted(
            (
                q.num,
                q.question,
                q.answer,
            )
            for q in questions
        )

        return normalize(new_questions) == normalize(old_questions)

    async def add_stages(self, skill_id: int, stages: list[StageAdd]):
        questions = []

        for stage in stages:
            new_stage = await self.add(
                StageAddDB(skill_id=skill_id, confirmation_type=stage.confirmation_type)
            )
            if stage.questions:
                stage_version = await self.stage_version_repository.add(
                    {"stage_id": new_stage.id}
                )

                for q in stage.questions:
                    questions.append(
                        {**q.model_dump(), "stage_version_id": stage_version.id}
                    )
        if questions:
            await self.question_repository.add_list(questions)

    async def _add_stage_version(
        self, old_stage: StageQuestionsSchema, new_stage: StageAdd
    ):
        if not self._questions_lists_equal(new_stage.questions, old_stage.questions):
            new_version = old_stage.last_version + 1 if old_stage.last_version else 1
            stage_version = await self.stage_version_repository.add(
                {"stage_id": old_stage.id, "version": new_version}
            )
            questions = []
            for q in new_stage.questions:
                questions.append(
                    {**q.model_dump(), "stage_version_id": stage_version.id}
                )
            if questions:
                await self.question_repository.add_list(questions)

    async def update_stages(
        self,
        skill_id: int,
        old_stages: list[StageQuestionsSchema],
        new_stages: list[StageUpdate],
    ):
        old_dict = {s.id: s for s in old_stages}
        new_dict = {s.id: s for s in new_stages if s.id}

        if del_stages := set(old_dict.keys()) - set(new_dict.keys()):
            await self.repository.soft_delete_list(list(del_stages))

        if add_stages := [s for s in new_stages if not s.id]:
            await self.add_stages(skill_id, add_stages)

        if upd_stages := [s for s in new_dict.values() if s.id in old_dict]:
            for stage in upd_stages:
                if stage.questions:
                    await self._add_stage_version(old_dict[stage.id], stage)

    async def update_questions(self, stage_id, stage: StageAdd):
        if not stage.questions:
            raise DataValidationError("Список вопросов не может быть пустым")

        old_stage: StageQuestionsSchema = await self.get_questions(stage_id)
        await self._add_stage_version(old_stage, stage)

        return await self.get_questions(stage_id)

    async def get_questions(self, stage_id):
        stage_questions: StageQuestionsSchema = await self.repository.get_questions(
            stage_id
        )
        if stage_questions is None:
            raise NotFoundException(f"Этап с id = {stage_id} не найден.")
        return stage_questions
