from pydantic import BaseModel, Field, ConfigDict, computed_field, model_validator, EmailStr
from schemas.users import SUser
from schemas.profiles import ProfileList


class UserProfileBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    profile_id: int
    current_level_id: int


class UserProfileAdd(BaseModel):
    user_id: int
    profile_id: int


class UserProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user: SUser
    profile: ProfileList

class UserProfileProgressList(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    patronymic: str
    email: EmailStr
    profile_title: str
    department_id: int | None = None
    department_name: str | None = None
    total_cnt: int
    completed_cnt: int

    @computed_field
    @property
    def progress(self) -> float:
        return self.completed_cnt / self.total_cnt if self.total_cnt else 0
