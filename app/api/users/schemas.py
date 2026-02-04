from pydantic import BaseModel, EmailStr, Field, ConfigDict, computed_field


class SRole(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_name: str


class SDepartment(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_name: str


class SPosition(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    position: str


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



class SUserFilter(BaseModel):
    id: int | None = None
    email: EmailStr | None = None
    department_id: int | None = None
    role_id: int | None = None
    position_id: int | None = None
