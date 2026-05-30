from pydantic import BaseModel, ConfigDict, EmailStr, computed_field

from schemas.profiles import ProfileList


class DepartmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_name: str


class DepartmentSchema(DepartmentBase):
    description: str | None = None


class DepartmentFilter(BaseModel):
    division_id: int


class Supervisor(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None = None
    position: str

    def full_name(self) -> str:
        patronymic = f"{self.patronymic[0] if self.patronymic else ''}"
        return f"{self.last_name} {self.first_name[0]}. {patronymic}."

    def name_with_email(self) -> str:
        return f"{self.full_name()} ({self.email})"


class DepartmentDetail(DepartmentBase):
    description: str | None = None
    supervisor: Supervisor | None = None
    profiles: list[ProfileList] | None = None

    @computed_field
    def supervisor_id(self) -> int | None:
        return self.supervisor.id if self.supervisor else None


class DepartmentAdd(BaseModel):
    department_name: str
    description: str | None = None


class DepartmentAddForm(DepartmentAdd):
    profiles: list[int] | None = None
    supervisor_id: int | None = None


class DepartmentUpdate(BaseModel):
    department_name: str | None = None
    description: str | None = None


class DepartmentUpdateForm(DepartmentUpdate):
    profiles: list[int] | None = None
    supervisor_id: int | None = None


class DivisionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    division_name: str


class DivisionSchema(DivisionBase):
    supervisor_id: int | None = None
    description: str | None = None


class DivisionAdd(BaseModel):
    division_name: str
    description: str | None = None


class DivisionAddForm(DivisionAdd):
    departments: list[int] | None = None


class DivisionUpdate(BaseModel):
    division_name: str | None = None
    description: str | None = None
    supervisor_id: int | None = None


class DivisionUpdateForm(DivisionUpdate):
    division_name: str | None = None
    supervisor_id: int | None = None
    departments: list[int] | None = None


class DivisionDetail(DivisionSchema):
    supervisor: Supervisor | None = None
    departments: list[DepartmentSchema] | None = None
