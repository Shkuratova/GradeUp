from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    computed_field,
    model_validator,
)
from db.models.types import ConfirmationTypes
from schemas.categories import CategoryBase


class SkillBase(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class SkillSchema(SkillBase):
    description: str | None = None
    literature: str | None = None
    categories: list[CategoryBase] | None = None
    stages: list[StageBase] | None = None

class SkillUpdate(BaseModel):
    skill: SkillSchema


class SkillAdd(BaseModel):
    title: str
    description: str | None = None
    literature: str | None = None


class QuestionAdd(BaseModel):
    num: int = Field(..., gt=0)
    question: str
    answer: str


class StageAddDB(BaseModel):
    skill_id: int
    confirmation_type: ConfirmationTypes


class StageAdd(BaseModel):
    confirmation_type: ConfirmationTypes
    questions: list[QuestionAdd] | None = None

    @model_validator(mode="after")
    def check_questions_num(self):
        if not self.questions:
            return self

        questions_nums = [q.num for q in self.questions]
        expected_nums = list(range(1, len(questions_nums) + 1))

        if sorted(questions_nums) != expected_nums:
            raise ValueError(
                f"Номера вопросов должны быть уникальными и идти последовательно от 1 до {len(questions_nums)}. "
            )
        return self


class StageUpdate(StageAdd):
    id: int | None = None


class SkillAddForm(BaseModel):
    skill: SkillAdd
    categories: list[int] = []
    stages: list[StageAdd] |  None = None

    @field_validator("stages", mode="after")
    @classmethod
    def check_stages(cls, v):
        if len(v) != len(set(s.confirmation_type for s in v)):
            raise ValueError(
                "Каждый тип подтверждения может входить в навык только один раз"
            )
        return v


class SkillUpdateForm(SkillAddForm):
    skill: SkillAdd
    stages: list[StageUpdate] | None = None


class SkillFilter(BaseModel):
    categories: list[int] | None = None
    id: int | None = None


class StageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    skill_id: int = Field(exclude=True)
    confirmation_type: ConfirmationTypes


class Question(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    num: int
    question: str
    answer: str


class StageVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    version: int
    questions: list[Question] | None = None


class StageSchema(StageBase):
    stage_versions: list[StageVersion] | None = Field(None, exclude=True)

    @computed_field
    @property
    def last_version(self) -> int | None:
        if self.stage_versions:
            return self.stage_versions[0].version
        return None


class StageVersionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    version: int


class SStageSchema(StageSchema):
    stage_versions: list[StageVersionBase] | None = Field(None, exclude=True)


class SkillStages(SkillSchema):
    stages: list[SStageSchema] | None = None


class StageQuestionsSchema(StageSchema):
    @computed_field
    @property
    def questions(self) -> list[Question] | None:
        if self.stage_versions:
            return self.stage_versions[0].questions


class SkillDetail(SkillSchema):
    stages: list[StageQuestionsSchema] | None = None
    categories: list[CategoryBase] | None = None
