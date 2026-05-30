from datetime import datetime

from pydantic import BaseModel, computed_field, ConfigDict, field_serializer

from db.models import ConfirmationTypes


class QuestionList(BaseModel):
    num: int
    question: str
    answer: str


class UserStage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    stage_id: int
    confirmation_type: ConfirmationTypes
    stage_version_id: int | None
    user_stage_id: int | None = None
    is_accepted: bool | None = None
    comment: str | None = None
    updated_at: datetime | None = None
    questions: list[QuestionList] | None = None

    @field_serializer("updated_at")
    def serialize_updated_at(self, value: datetime | None):
        if value:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return None


class SkillProgressSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    skill_id: int
    title: str
    description: str | None = None
    literature: str | None = None
    is_accepted: bool | None = None
    stages: list[UserStage]


class StageProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    stage_id: int
    stage_version_id: int | None = None
    confirmation_type: ConfirmationTypes
    is_accepted: bool | None = None
    comment: str | None = None
    updated_at: datetime | None = None

    @field_serializer("updated_at")
    def serialize_updated_at(self, value: datetime | None):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


class SkillProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    is_accepted: bool | None = None
    stage_cnt: int
    accepted_stages: int = 0

    @computed_field
    def skill_progress(self) -> float:
        if self.stage_cnt:
            return round(self.accepted_stages / self.stage_cnt * 100)
        return 0


class LevelProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    num: int
    level_name: str
    is_closed: bool | None = None
    skills: list[SkillProgress] | None = None

    @computed_field
    def level_progress(self) -> float:
        if self.skills:
            accepted = sum(s.accepted_stages for s in self.skills)
            total = sum(s.stage_cnt for s in self.skills)
            return round(accepted / total * 100)
        return 0


class ProfileProgress(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    profile_id: int
    title: str
    current_level_id: int
    description: str | None = None
    levels: list[LevelProgress] | None = None

    @computed_field
    def profile_progress(self) -> float | None:
        if self.levels:
            accepted = sum(l.is_closed == True for l in self.levels)
            return round(accepted / len(self.levels) * 100)
        return 0

    @computed_field
    def ready_gradeup(self) -> bool | None:
        if self.levels:
            current_lvl = next(l for l in self.levels if l.id == self.current_level_id)
            if current_lvl.level_progress == 100:
                return True
        return False
