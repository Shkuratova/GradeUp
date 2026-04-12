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
    first_name: str
    last_name: str
    position: str | None
    patronymic: str | None

    @computed_field
    def role_name(self) -> str:
        return self.role.role_name

    @computed_field
    def department_name(self)-> str | None:
        return self.department.department_name if self.department else None

    @computed_field
    def department_id(self) -> int | None:
        return self.department.id if self.department else None


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
    profile_id: int | None = None
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
    profile_id: int | None = None
    role_id: int = Field(default=1)


class UserRegistration(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None = None
    department_id: int | None = None
    position: str | None = None
    profile_id: int| None = None
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





class SUserFullInfo(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    patronymic: str | None
    department_id: int | None
    department: SDepartment | None = Field(None,)
    profile_id: int | None = None
    role: SRole | None = Field(default=None, exclude=True)

    # @computed_field
    # def department_name(self) -> str | None:
    #     return self.department and self.department.department_name

    @computed_field
    def role_name(self) -> str | None:
        return self.role and self.role.role_name


class SUserFilter(BaseModel):
    id: int | None = None
    email: EmailStr | None = None
    department_id: int | None = None
    role_id: int | None = None
    position: str | None = None
