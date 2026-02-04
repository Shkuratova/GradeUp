from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    model_validator,
    Field,
)


class EmailModel(BaseModel):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserAuth(EmailModel):
    password: str


class UserSchema(EmailModel):
    id: int
    role_id: int


class SUserRole(BaseModel):
    id: int
    role_id: int


class UserInfo(EmailModel):
    first_name: str | None
    last_name: str | None
    patronymic: str | None
    role_id: int
    department_id: int | None = None


class SUserAdd(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    position_id: int | None = None
    department_id: int | None = None
    role_id: int = Field(default=1)


class SUserRegistration(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None = None
    department_id: int
    position_id: int

    password: str
    confirm_password: str = Field(exclude=True)

 





