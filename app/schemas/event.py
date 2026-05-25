from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, computed_field, EmailStr, field_serializer

from db.models.types import EventType, TargetType
from schemas.users import UserSchema
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
    actor: UserSchema = Field(exclude=True)
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




