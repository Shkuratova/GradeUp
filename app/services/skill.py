from sqlalchemy.ext.asyncio import AsyncSession

from db.models.skills import StageVersion
from db.repository import QuestionRepository
from exceptions.common import NotFoundException, DataValidationError
from services.base import BaseService
from db.repository import (
    SkillRepository,
    CategoryRepository,
    LevelSkillRepository,
    SkillCategoryRepository,
    StageVersionRepository,
    StageRepository,
)
from pydantic import BaseModel
from schemas.skills import (
    SkillFilter,
    SkillDetail,
    SkillUpdateForm,
    SkillAddForm,
    SkillStages,
    SkillUpdate,
    StageSchema,
    StageQuestionsSchema,
    StageAdd,
)


class SkillService(BaseService):

    entity_name = "Навык"
    unique_fields = ["title"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = SkillRepository(session)
        self.stage_repository = StageRepository(session)
        self.stage_version_repository = StageVersionRepository(session)
        self.question_repository = QuestionRepository(session)

    async def get_all_by_categories(self, filter_model: SkillFilter):
        if filter_model.categories:
            res = await self.repository.get_all_by_categories(filter_model.categories)
        else:
            res = await self.get_all()
        return res

    async def get_skills_stages(self, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_none=True)
        res = await self.repository.get_stages(filter_dict)
        return res

    async def get_skill_with_questions(self, skill_id: int):
        skill = await self.repository.get_last_skill_with_questions(skill_id)
        return SkillDetail.model_validate(skill)

    async def _add_stages(self, skill_id: int, stages):
        questions = []
        for stage in stages:
            new_stage = await self.stage_repository.add(
                {"skill_id": skill_id, "confirmation_type": stage.confirmation_type}
            )
            stage_version = await self.stage_version_repository.add(
                {"stage_id": new_stage.id}
            )
            for q in stage.questions:
                q.stage_version_id = stage_version.id
                questions.append(q)

        await self.question_repository.add_list(questions)

    async def add_skill(self, model: SkillAddForm):
        new_skill = await self.repository.add(model.skill.model_dump(exclude_none=True))

        if not model.stages:
            return new_skill

        await self._add_stages(new_skill.id, model.stages)
        return new_skill

    async def update_by_id(self, skill_id: int, model: SkillUpdateForm):
        old_skill: SkillStages = await self.repository.get_stages({}, skill_id)
        if old_skill is None:
            raise NotFoundException(f"Навык с id = {skill_id} не найден.")
        old_skill = SkillStages.model_validate(old_skill)
        skill = model.skill
        res = await super().update_by_id(skill_id, skill)
        exist_stages_dict = {s.id: s for s in old_skill.stages}
        new_stages_ids = set()
        stages_add = []
        stages_upd = []
        for stage in model.stages:
            if stage.id is None:
                stages_add.append(stage)
            else:
                new_stages_ids.add(stage.id)
                if stage.id in exist_stages_dict:
                    stages_upd.append(stage)

        stage_del = [
            stage_id
            for stage_id in exist_stages_dict.keys()
            if stage_id not in new_stages_ids
        ]
        if stage_del:
            await self.stage_repository.soft_delete_list(stage_del)
        if stages_add:
            await self._add_stages(skill_id, stages_add)
        if stages_upd:
            questions = []
            for stage in stages_upd:
                new_version = exist_stages_dict[stage.id].last_version + 1
                stage_version = await self.stage_version_repository.add(
                    {"stage_id": stage.id, "version": new_version}
                )
                for q in stage.questions:
                    q.stage_version_id = stage_version.id
                    questions.append(q)
            await self.question_repository.add_list(questions)
        return res

    async def partial_update(self, skill_id: int, model: SkillUpdateForm):
        skill = model.skill
        res = await super().update_by_id(skill_id, skill)


class StageService(BaseService):
    entity_name = "Этап подтверждения"
    repository_factory = StageRepository
    # unique_fields = []

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = StageRepository(session)
        self.stage_version_repository = StageVersionRepository(session)
        self.question_repository = QuestionRepository(session)

    async def update_questions(self, stage_id, stage: StageAdd):
        if not stage.questions:
            raise DataValidationError("Список вопросов не может быть пустым")

        old_stage = await self.get_by_id(stage_id)

        new_stage_version = await self.stage_version_repository.add_new_version(stage_id)
        questions = [
            {
                **q.model_dump(exclude_none=True),
                "stage_version_id": new_stage_version.id,
            }
            for q in stage.questions
        ]
        res = await self.question_repository.add_list(questions)

    async def get_questions(self, stage_id):
        stage_questions: StageQuestionsSchema = await self.repository.get_questions(
            stage_id
        )
        if stage_questions is None:
            raise NotFoundException(f"Этап с id = {stage_id} не найден.")
        return stage_questions


class LevelSkillService(BaseService):
    unique_fields = ["skill_id", "profile_level_id"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = LevelSkillRepository(session)


class CategoryService(BaseService):
    entity_name = "Категория"
    unique_fields = ["category_name"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = CategoryRepository(session)


class SkillCategoryService(BaseService):
    unique_fields = ["skill_id", "category_id"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = SkillCategoryRepository(session)
