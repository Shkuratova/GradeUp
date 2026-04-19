from db.repository.department import DepartmentRepository
from db.uow import unit_of_work
from exceptions.common import AlreadyExistException
from schemas.departments import SDepartment, DepartmentUpdate
from services.base import BaseService


class DepartmentService(BaseService):
    entity_name = "Отдел"
    unique_fields = ["department_name"]
    repository_factory = DepartmentRepository


