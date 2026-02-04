from pydantic import BaseModel, ConfigDict, Field, computed_field
from app.api.users import SPosition
from datetime import datetime


class SProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    position_level: str
    position: SPosition = Field(exclude=True)

    @computed_field
    def position_id(self) -> int:
        return self.position.id

    @computed_field
    def position_name(self) -> str:
        return self.position.position


class SProfileFilter(BaseModel):
    position_id: int | None = None
    position_name: str | None = None
    position_level: str | None  = None




class SSkillBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str

class SSkill(SSkillBase):
    id: int
    creator_id: int


class SSkillInfo(SSkillBase):
    num_stages: int
    creator: str
    created_at: datetime



class SCertification(BaseModel):
    model_config = ConfigDict(from_attributes=True)