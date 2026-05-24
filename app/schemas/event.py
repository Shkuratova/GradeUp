from pydantic import BaseModel, Field, ConfigDict, computed_field, EmailStr, field_serializer
from datetime import datetime
from typing import Any

from db.models import ConfirmationTypes
from db.models.events import EventType, TargetType
from schemas.users import UserFIO
from utils.roles import UserRole


class EventBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    actor_id: int
    access_scope: str
    target_id: int
    target_type: TargetType
    event_type: EventType

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime, _info):
        return value.strftime("%Y-%m-%d %H:%M:%S")



class EventAdd(BaseModel):
    actor_id: int
    access_scope: str
    target_id: int
    target_type: TargetType
    event_type: EventType
    message: str
    payload: dict


class EventSchema(EventBase):
    actor: UserFIO = Field(exclude=True)
    message: str | None = None

    @computed_field
    def actor_name(self) -> str:
        return self.actor.name_with_email()

class EventFilter(BaseModel):
    actor_id: int | None = None
    access_scope: UserRole | None = None
    target_id: int | None = None
    target_type: TargetType | None = None
    event_type: EventType | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class UserPayloadBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: int
    full_name: str
    email: EmailStr

class RegistrationPayload(UserPayloadBase):
    department_id: int | None = None

class RegistrationEvent(EventAdd):
    payload: RegistrationPayload


class SetProfilePayload(UserPayloadBase):
    profile_id: int
    title: str
    department_id: int | None

class SetProfileEvent(EventAdd):
    payload: SetProfilePayload

class EvaluatePayload(UserPayloadBase):
    user_stage_id: int
    skill_id: int
    stage_id: int
    confirmation_type: ConfirmationTypes
    is_accepted: bool

class EvaluateEvent(EventAdd):
    payload: EvaluatePayload

class GradeUpPayload(UserPayloadBase):
    user_profile_id: int
    old_profile_level_id: int
    new_profile_level_id: int

class GradeUpEvent(EventAdd):
    payload: GradeUpPayload

class ScheduleMeetingPayload(UserPayloadBase):
    examiner_id: int
    examiner_email: EmailStr
    stage_id: int
    started_at: datetime
    location: str
    duration: int

class ScheduleMeetingEvent(EventAdd):
    payload: ScheduleMeetingPayload


