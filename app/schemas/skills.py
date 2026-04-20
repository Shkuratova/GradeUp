from pydantic import BaseModel, Field, ConfigDict, field_validator
from schemas.users import UserInfo
from db.models.skills import ConfirmationTypes


class SkillBase(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class SkillAdd(BaseModel):
    title: str
    creator_id: int = Field(default=1)
    description: str | None = None
    literature: str | None = None


class SkillUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    literature: str | None = None


class SkillInfo(SkillBase):
    description: str | None = None
    literature: str | None = None


class StageBase(BaseModel):
    id: int
    skill_id: int
    confirmation_type: ConfirmationTypes
    model_config = ConfigDict(from_attributes=True)


class StageAdd(BaseModel):
    skill_id: int = Field(default=1)
    confirmation_type: ConfirmationTypes


class StageItem(BaseModel):
    id: int
    confirmation_type: ConfirmationTypes

class SkillStages(SkillInfo):
    # creator: UserInfo = Field(exclude=True)
    stages: list[StageItem]

    # @computed_field
    # def created_by(self) -> str:
    #     return f"{self.creator.last_name} {self.creator.first_name} {self.creator.patronymic if self.creator.patronymic else ''}"


class SkillFilter(BaseModel):
    creator_id: int | None = None


class SkillStageFilter(BaseModel):
    confirmation_type: ConfirmationTypes | None = None


class SSkillAdd(BaseModel):
    skill: SkillAdd
    stages: list[ConfirmationTypes] = []
    creator_id: int = Field(default=1)
    @field_validator('stages', mode='after')
    @classmethod
    def check_stages(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Каждый тип подтверждения может входить в навык только один раз')
        return v