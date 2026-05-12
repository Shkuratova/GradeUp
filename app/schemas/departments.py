from pydantic import BaseModel, Field, ConfigDict, model_validator

from schemas.profiles import ProfileList
from schemas.users import UserFIO


class DepartmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_name: str

class DepartmentDetail(DepartmentBase):
    supervisor: UserFIO | None = None
    profiles: list[ProfileList] = []

class DepartmentAdd(BaseModel):
    department_name: str


class DepartmentUpdate(DepartmentAdd):
    department_name: str | None  = None
    supervisor_id: int | None = None
    profiles: list[int] = []


class DivisionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    division_name: str

class DivisionAdd(BaseModel):
    division_name: str

class DivisionUpdate(BaseModel):
    division_name: str | None = None
    supervisor_id: int | None = None
    departments: list[int] | None = None

class DivisionDetail(DivisionBase):
    supervisor: UserFIO
    departments: list[DepartmentBase]
