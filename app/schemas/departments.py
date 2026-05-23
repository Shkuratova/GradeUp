from pydantic import BaseModel, Field, ConfigDict, model_validator

from schemas.profiles import ProfileList
from schemas.users import UserFIO


class DepartmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_name: str
    supervisor_id: int | None = None

class DepartmentSchema(DepartmentBase):
    description: str | None = None

class DepartmentFilter(BaseModel):
    division_id: int

class DepartmentDetail(DepartmentBase):
    description: str | None = None
    supervisor: UserFIO | None = None
    profiles: list[ProfileList] | None = None

class DepartmentAdd(BaseModel):
    department_name: str
    description: str | None = None
    supervisor_id: int | None = None

class DepartmentAddForm(DepartmentAdd):
    profiles: list[int] | None = None


class DepartmentUpdate(BaseModel):
    department_name: str | None  = None
    description : str | None = None
    supervisor_id: int | None = None

class DepartmentUpdateForm(DepartmentUpdate):
    profiles: list[int] | None = None



class DivisionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    supervisor_id: int | None = None
    division_name: str


class DivisionSchema(DivisionBase):
    description: str | None = None


class DivisionAdd(BaseModel):
    division_name: str
    description: str | None = None

class DivisionAddForm(DivisionAdd):
    departments: list[int]  | None = None

class DivisionUpdate(BaseModel):
    division_name: str | None = None
    description: str | None = None
    supervisor_id: int | None = None

class DivisionUpdateForm(DivisionUpdate):
    division_name: str | None = None
    supervisor_id: int | None = None
    departments: list[int] | None = None

class DivisionDetail(DivisionBase):
    supervisor: UserFIO | None = None
    departments: list[DepartmentSchema] | None = None
