from datetime import datetime, timezone

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    computed_field,
    model_validator,
    EmailStr,
    field_serializer,
)
from db.models.types import CertificationStatus, CertificationRole, ConfirmationTypes
from exceptions.common import DataValidationError
from schemas.profiles import SkillList
from schemas.users import UserFIO, UserBase, UserInfo


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
    id: int
    user_id: int
    role: CertificationRole


class Participant(ParticipantBase):

    user: UserFIO = Field(exclude=True)

    @computed_field
    def full_name(self) -> str:
        return self.user.full_name()

    @computed_field
    def email(self) -> EmailStr:
        return self.user.email

class MeetingStage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    confirmation_type: ConfirmationTypes
    skill: SkillList


class MeetingStageVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stage_id: int
    stage: MeetingStage


class UserStage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stage_version: MeetingStageVersion


class MeetingDetail(BaseModel):
    id: int
    started_at: datetime
    location: str
    duration: int
    description: str | None = None
    status: CertificationStatus
    participants: list[Participant] = Field(exclude=True)
    user_stage: UserStage = Field(exclude=True)

    @computed_field
    def user_stage_id(self) -> int:
        return self.user_stage.id

    @computed_field
    def stage_id(self) -> int:
        return self.user_stage.stage_version.stage_id

    @computed_field
    def stage_version_id(self) -> int:
        return self.user_stage.stage_version.id

    @computed_field
    def confirmation_type(self) -> ConfirmationTypes:
        return self.user_stage.stage_version.stage.confirmation_type

    @computed_field
    def skill_title(self) -> str:
        return self.user_stage.stage_version.stage.skill.title

    @computed_field
    def student(self) -> Participant:
        participant = next(
            (p for p in self.participants if p.role == CertificationRole.student), None
        )
        return participant

    @computed_field
    def examiner(self) -> Participant | None:
        participant = next(
            (p for p in self.participants if p.role == CertificationRole.examiner), None
        )
        if participant is None:
            return None
        return participant

    @field_serializer("started_at")
    def serialize_started_at(self, value: datetime, _info):
        return value.strftime("%Y-%m-%d %H:%M:%S")


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
    duration: int = Field(..., gt=0)
    description: str | None = None
    student_id: int
    examiner_id: int


class MeetingUpdateForm(BaseModel):
    id: int
    stage_id: int
    started_at: datetime
    location: str
    duration: int = Field(..., gt=0)
    description: str | None = None
    examiner_id: int | None = None


class MeetingFilters(BaseModel):
    id: int | None = None
    user_id: int | None = None
    user_role: CertificationRole | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: CertificationStatus | None = None
    stage_id: int | None = None
    confirmation_type: ConfirmationTypes | None = None
    skill_id: int | None = None
    departments_id: list[int] | None = None

    @model_validator(mode="after")
    def check_filters(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("Дата начала не может быть больше даты окончания.")
        return self

class MeetingAddResult(BaseModel):
    meeting: MeetingDetail
    student: UserInfo
