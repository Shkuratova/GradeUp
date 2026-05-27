from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict,
    computed_field, model_validator
)

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
    department_id: int | None = None
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


class DepartmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_name: str

class DivisionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    division_name: str

class UserInfo(UserSchema):
    role: RoleSchema = Field(exclude=True)
    department: DepartmentSchema | None = Field(None, exclude=True)
    managed_division: DivisionSchema | None = Field(None, exclude=True)
    managed_department: DepartmentSchema | None = Field(None, exclude=True)
    role_id: int
    position: str | None
    password: str = Field(None, exclude=True)

    def is_supervisor(self) -> bool:
        return self.managed_division is not None or self.managed_department is not None

    @computed_field
    @property
    def roles(self) -> list[str]:
        roles = {self.role.role_name}

        if self.is_supervisor():
            roles.add(UserRole.SUPERVISOR)

        return list(roles)


    @computed_field
    def role_name(self) -> str:
        return self.role.role_name

    @computed_field
    def department_name(self) -> str | None:
        return self.department.department_name if self.department else None

    @computed_field
    def division_id(self) -> int | None:
        return self.managed_division.id if self.managed_division else None

    @computed_field
    def managed_division_id(self) -> str | None:
        return self.managed_division.id if self.managed_division else None

    @computed_field
    def managed_division_name(self) -> str | None:
        return self.managed_division.division_name if self.managed_division else None
