from pydantic import BaseModel, Field, ConfigDict, computed_field
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


class StageAdd(StageBase):
    creator_id: int


class SkillStages(SkillInfo):
    creator: UserInfo = Field(exclude=True)
    skills: list[StageBase]

    @computed_field
    def created_by(self) -> str:
        return f"{self.creator.last_name} {self.creator.first_name} {self.creator.patronymic if self.creator.patronymic else ''}"


class SkillFilter(BaseModel):
    creator_id: int | None = None