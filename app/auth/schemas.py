from pydantic import BaseModel, EmailStr, ConfigDict, model_validator, Field, computed_field
from app.auth.utils import hash_password
from app.exceptions import PasswordDontMatchException


class EmailModel(BaseModel):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserAuth(EmailModel):
    password: str


class UserSchema(EmailModel):
    id: int
    role_id: int



class SUserRole(BaseModel):
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
    first_name: str | None  = Field(default=None)
    last_name: str | None = Field(default=None)
    patronymic: str | None = Field(default=None)
    position_id: int | None = Field(default=None)
    department_id: int | None = Field(default=None)
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

    @model_validator(mode="after")
    def check_password(self):
        if self.password != self.confirm_password:
            raise PasswordDontMatchException
        self.password = hash_password(self.password)
        return self 
    

class SPosition(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int 
    position: str 

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
    first_name: str | None = Field(exclude=True)
    last_name: str | None = Field(exclude=True)
    patronymic: str | None = Field(exclude=True)
    department: SDepartment | None = Field(None, exclude=True)
    position: SPosition | None = Field(None, exclude=True)
    role: SRole | None = Field(default=None, exclude=True)

    @computed_field
    def position_name(self) -> str | None:
        return self.position.position if self.position else None
    
    @computed_field
    def position_name(self) -> str | None:
        return self.position and self.position.position
    
    @computed_field
    def department_name(self) -> str | None:
        return self.department and self.department.department_name
    
    @computed_field
    def role_name(self) -> str | None:
        return self.role and self.role.role_name
    
    @computed_field
    def full_name(self) -> str:
        fio = [self.last_name, self.first_name, self.patronymic]
        return " ".join(filter(None, fio))