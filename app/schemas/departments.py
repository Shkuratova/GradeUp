from pydantic import BaseModel, Field, ConfigDict


class DepartmentBase(BaseModel):
    id: int

class SDepartment(DepartmentBase):
    department_name: str

class DepartmentAdd(BaseModel):
    department_name: str

class DepartmentUpdate(BaseModel):
    department_name: str
