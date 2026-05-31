from datetime import datetime

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
from schemas.profiles import SkillList
from schemas.skills import StageList, Question
from schemas.users import UserSchema, UserInfo


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

    user: UserSchema = Field(exclude=True)

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


class UserStage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stage_version_id: int
    skill: SkillList
    stage: StageList


class MeetingDetail(BaseModel):
    id: int
    started_at: datetime
    location: str
    duration: int
    description: str | None = None
    status: CertificationStatus
    is_approved: bool
    ended_at: datetime | None = None
    participants: list[Participant] = Field(exclude=True)
    user_stage: UserStage = Field(exclude=True)

    @computed_field
    def user_stage_id(self)-> int:
        return self.user_stage.id

    @computed_field
    def stage_id(self) -> int:
        return self.user_stage.stage.id

    @computed_field
    def stage_version_id(self) -> int:
        return self.user_stage.stage_version_id

    @computed_field
    def confirmation_type(self) -> ConfirmationTypes:
        return self.user_stage.stage.confirmation_type

    @computed_field
    def skill_id(self) -> int:
        return self.user_stage.skill.id

    @computed_field
    def title(self) -> str:
        return self.user_stage.skill.title

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

    @field_serializer("ended_at")
    def serialize_ended_at(self, value: datetime, _info):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None




class MeetingAdd(BaseModel):
    stage_version_id: int = Field(default=1)
    started_at: datetime
    location: str
    duration: int


class MeetingAddForm(BaseModel):
    stage_id: int
    started_at: datetime
    location: str
    duration: int = Field(..., gt=0)
    student_id: int
    examiner_id: int


class MeetingUpdateForm(BaseModel):
    stage_id: int
    started_at: datetime
    location: str
    duration: int = Field(..., gt=0)
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

class MeetingMaterial(BaseModel):
    skill_id: int
    title: str
    literature: str | None = None
    description: str | None = None

class MeetingQuestions(MeetingMaterial):
    questions: list[Question] | None = None
