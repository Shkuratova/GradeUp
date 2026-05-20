from pydantic import BaseModel, Field, ConfigDict, model_validator

from schemas.profiles import ProfileList
from schemas.users import UserFIO


class DepartmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_name: str

class DepartmentSchema(DepartmentBase):
    description: str | None = None

class DepartmentDetail(DepartmentBase):
    description: str | None = None
    supervisor: UserFIO | None = None
    profiles: list[ProfileList] = []

class DepartmentAdd(BaseModel):
    department_name: str
    description: str | None = None
    supervisor_id: int | None

class DepartmentAddForm(DepartmentAdd):
    profiles: list[int] = []


class DepartmentUpdate(BaseModel):
    department_name: str | None  = None
    description : str | None = None
    supervisor_id: int | None = None

class DepartmentUpdateForm(DepartmentUpdate):
    profiles: list[int] = []



class DivisionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    division_name: str


class DivisionAdd(BaseModel):
    division_name: str
    description: str | None = None
    supervisor_id: int | None = None

class DivisionAddForm(DivisionAdd):
    departments: list[int] = []

class DivisionUpdate(BaseModel):
    division_name: str | None = None
    description: str | None = None
    supervisor_id: int | None = None

class DivisionUpdateForm(DivisionUpdate):
    division_name: str | None = None
    supervisor_id: int | None = None
    departments: list[int] = []

class DivisionDetail(DivisionBase):
    supervisor: UserFIO
    departments: list[DepartmentSchema]
