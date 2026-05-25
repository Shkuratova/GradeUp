from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer

from datetime import datetime
from db.models import ConfirmationTypes
from schemas.profiles import SkillList
from schemas.skills import StageList


class EvaluationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_accepted: bool = False
    stage_version_id: int

class EvaluationSchema(EvaluationBase):
    comment: str | None = None
    updated_at: datetime
    skill: SkillList = Field(exclude=True)
    stage: StageList = Field(exclude=True)

    @computed_field
    def skill_id(self) -> int:
        return self.skill.id

    @computed_field
    def title(self) -> str:
        return self.skill.title

    @computed_field
    def stage_id(self) -> int:
        return self.stage.id

    @computed_field
    def confirmation_type(self) -> ConfirmationTypes:
        return self.stage.confirmation_type

    @field_serializer("updated_at")
    def serialize_updated_at(self, value: datetime, _info):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    def evaluation(self) -> str:
        return 'Зачтено' if self.is_accepted else 'Не зачтено'