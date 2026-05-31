from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict,
    computed_field, model_validator
)

from db.models.types import DepartmentRole
from utils.roles import UserRole


class RoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_name: UserRole


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EmailModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr

class ResetPassword(BaseModel):
    password: str
    confirm_password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


class UserAuth(EmailModel):
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    position: str | None = None
    role_id: int = Field(default=1)


class UserRegistration(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None = None
    department_id: int | None = None
    position: str | None = None
    password: str
    confirm_password: str = Field(exclude=True)



class UserUpdateBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    email: EmailStr | None = None
    position: str | None = None
    model_config = ConfigDict(extra="forbid")


class UserUpdateAdmin(UserUpdateBase):
    role_id: int | None = None
    department_id: int | None = None


class UserSchema(UserBase):
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None = None
    role_id: int
    position: str | None = None
    department_id: int | None = None

    def full_name(self) -> str:
        patronymic = f"{self.patronymic[0] if self.patronymic else ''}"
        return f'{self.last_name} {self.first_name[0]}. {patronymic}.'

    def name_with_email(self) ->str:
        return f"{self.full_name()} ({self.email})"


class UserFilter(BaseModel):
    id: int | None = None
    email: EmailStr | None = None
    departments_id: list[int] | None = None
    division_id: int | None = None
    role_id: int | None = None
    position: str | None = None
    only_subordinates: bool | None = Field(None, exclude=True)


class UserInfo(UserSchema):
    role_id: int
    role_name: str
    department_id: int | None = None
    department_name: str | None = None
    department_role: DepartmentRole | None = Field(None, exclude=True)
    managed_division_id: int | None = None
    managed_division_name: str | None = None

    position: str | None
    password: str = Field(None, exclude=True)

    def is_department_supervisor(self) -> bool:
        return self.department_role and self.department_role == DepartmentRole.SUPERVISOR

    def is_division_supervisor(self)->bool:
        return self.managed_division_id is not None

    def is_spo(self):
        return self.role_name == UserRole.SPO

    def is_admin(self):
        return self.role_name == UserRole.ADMIN

    @computed_field
    @property
    def roles(self) -> list[str]:
        roles = {self.role_name}
        if self.is_division_supervisor() or self.is_department_supervisor():
            roles.add(UserRole.SUPERVISOR)

        return list(roles)
