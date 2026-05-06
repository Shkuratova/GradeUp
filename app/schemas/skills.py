from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from db.models.types import ConfirmationTypes


class SkillBase(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class SkillSchema(SkillBase):
    description: str | None = None
    literature: str | None = None


class SkillUpdate(BaseModel):
    skill: SkillSchema


class SkillAdd(BaseModel):
    title: str
    creator_id: int = Field(default=1)
    description: str | None = None
    literature: str | None = None


class QuestionAdd(BaseModel):
    num: int = Field(..., gt=0)
    question: str
    answer: str
    stage_version_id: int = Field(default=1)


class StageAdd(BaseModel):
    confirmation_type: ConfirmationTypes
    questions: list[QuestionAdd]


class StageUpdate(StageAdd):
    id: int | None = None


class SkillAddForm(BaseModel):
    skill: SkillAdd
    stages: list[StageAdd]

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
    stages: list[StageUpdate]


class SkillFilter(BaseModel):
    categories: list[int] = []
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
        if self.stage_versions is not None:
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
        return self.stage_versions[0].questions


class SkillDetail(SkillSchema):
    stages: list[StageQuestionsSchema]
