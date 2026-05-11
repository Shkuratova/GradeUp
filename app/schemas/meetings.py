from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, computed_field, model_validator
from db.models.types import CertificationStatus, CertificationRole, ConfirmationTypes
from schemas.profiles import SkillList
from schemas.users import UserFIO


class MeetingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stage_version_id: int
    status: CertificationStatus
    duration: int
    location: str
    started_at: datetime
    created_by: int


class ParticipantBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    role: CertificationRole


class Participant(ParticipantBase):
    user: UserFIO = Field(exclude=True)

    @computed_field
    def first_name(self) -> str:
        return self.user.first_name

    @computed_field
    def last_name(self) -> str:
        return self.user.last_name

    @computed_field
    def patronymic(self) -> str:
        return self.user.patronymic


class MeetingStage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    confirmation_type: ConfirmationTypes
    skill: SkillList


class MeetingStageVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stage: MeetingStage


class MeetingDetail(BaseModel):
    id: int
    started_at: datetime
    location: str
    duration: int
    description: str | None = None
    status: CertificationStatus
    participants: list[Participant]
    stage_version: MeetingStageVersion = Field(exclude=True)

    @computed_field
    def stage_version_id(self) -> int:
        return self.stage_version.id

    @computed_field
    def confirmation_type(self) -> ConfirmationTypes:
        return self.stage_version.stage.confirmation_type

    @computed_field
    def skill_title(self) -> str:
        return self.stage_version.stage.skill.title


class MeetingAdd(BaseModel):
    stage_version_id: int = Field(default=1)
    started_at: datetime
    location: str
    duration: int
    description: str | None = None


class MeetingAddForm(BaseModel):
    stage_id: int
    started_at: datetime
    location: str
    duration: int
    description: str | None = None
    student_id: int
    examiner_id: int

class MeetingUpdateForm(MeetingAddForm):
    id: int

class MeetingFilters(BaseModel):
    id: int | None = None
    user_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime = Field(datetime.now())
    status: CertificationStatus | None = None
    confirmation_type: ConfirmationTypes | None = None
    skill_id: int | None = None
    department_id: int | None = None

    @model_validator(mode="after")
    def check_filters(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("Дата начала не может быть больше даты окончания.")
        return self
