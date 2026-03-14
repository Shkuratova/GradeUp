from db.repository.department import department_repository_factory, DepartmentRepository
from db.uow import unit_of_work
from exceptions.common import AlreadyExistException
from schemas.departments import SDepartment, DepartmentUpdate
from services.base import BaseService


class DepartmentService(BaseService):
    entity_name = "Отдел"
    unique_field = "department_name"


department_service = DepartmentService(department_repository_factory)
