from pydantic import BaseModel, Field, computed_field, ConfigDict, field_serializer
from datetime import datetime


class StageVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stage_id: int

class StageProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_accepted: bool
    comment: str | None = None
    stage_version: StageVersion = Field(exclude=True)
    updated_at: datetime

    @computed_field
    def stage_id(self) -> int:
        return self.stage_version.stage_id
    @computed_field
    def stage_version_id(self) -> int:
        return self.stage_version.id

    @field_serializer("updated_at")
    def serialize_started_at(self, value: datetime, _info):
        return value.strftime("%Y-%m-%d %H:%M:%S")


class SkillProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: int
    is_accepted: bool
    stages: list[StageProgress]

class ProfileUser(BaseModel):
    user_skills: list[SkillProgress]

class ProfileProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    profile_id: int
    user_id: int
    current_level_id: int
    user: ProfileUser = Field(exclude=True)
    @computed_field
    def skills(self) -> list[SkillProgress] | None:
        return self.user.user_skills
