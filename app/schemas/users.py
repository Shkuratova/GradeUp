from pydantic import BaseModel, Field, EmailStr, ConfigDict, computed_field, model_validator


class UserBase(BaseModel):
    id:int 
    model_config = ConfigDict(from_attributes=True)


class EmailModel(BaseModel):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class UserInfo(UserBase, EmailModel):
    role: SRole = Field(exclude=True)
    department: SDepartment | None = Field(None, exclude=True)
    managed_division: SDivision | None = Field(None, exclude=True)
    first_name: str
    last_name: str
    patronymic: str | None
    position: str | None
    accessed_departments: list[int] | None = Field(None, exclude=True)

    password: str = Field(exclude=True)
    @computed_field
    def role_name(self) -> str:
        return self.role.role_name

    @computed_field
    def department_name(self)-> str | None:
        return self.managed_department.department_name

    @computed_field
    def department_id(self) -> int | None:
        return self.department.id if self.department else None

    @computed_field
    def division_id(self) -> int | None:
        return self.managed_division.id if self.managed_division else None

    @computed_field
    def division_name(self) -> str | None:
        return self.managed_division.division_name if self.managed_division else None


class UserAuth(EmailModel):
    password: str


class UserRole(UserBase):
    role_name: str


class UserUpdateBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    email: EmailStr | None = None

    model_config = ConfigDict(extra="forbid")

class UserUpdateSupervisor(UserUpdateBase):
    profile_id: int | None = None

class UserUpdateAdmin(UserUpdateSupervisor):
    role_id: int | None = None
    department_id: int | None  = None


class SUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None
    role_id: int
    position: str  | None
    department_id: int | None = None


class UserFullInfo(EmailModel, UserRole):
    first_name: str
    last_name: str
    patronymic: str | None
    department_id: int
    department_name: str

class UserFilter(BaseModel):
    email: EmailStr | None
    department_id: int | None
    role_id: int | None
    position: str | None


class SetUserRole(BaseModel):
    id: int = Field(exclude=True)
    role_id: int

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

class SRole(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_name: str


class SDepartment(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_name: str

class SDivision(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    division_name: str


class SUserFullInfo(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    patronymic: str | None
    department_id: int | None

    department: SDepartment | None = Field(None, exclude=True)
    managed_department: SDepartment | None = Field(exclude=True)
    managed_division: SDivision | None = Field(exclude=True)
    role: SRole | None = Field(default=None, exclude=True)

    @computed_field
    def department_name(self) -> str | None:
        if self.managed_department:
            return self.managed_department.department_name
        return self.department and self.department.department_name

    @computed_field
    def managed_division_name(self) -> str | None:
        if self.managed_division:
            return self.managed_division.division_name


    @computed_field
    def role_name(self) -> str | None:
        return self.role and self.role.role_name


class SUserFilter(BaseModel):
    id: int | None = None
    email: EmailStr | None = None
    departments_id: list[int] | None = None
    role_id: int | None = None
    position: str | None = None
    only_subordinates: bool = Field(False, exclude=True)


class UserFIO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    patronymic: str | None = None
    # department_id: int
    # department_name: str
