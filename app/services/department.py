from db.repository.department import department_repository_factory, DepartmentRepository
from db.uow import unit_of_work
from exceptions.common import NotFoundException, AlreadyExistException
from schemas.departments import SDepartment, DepartmentUpdate
from services.base import BaseService

class DepartmentService(BaseService):
    entity_name = "Отдел"

    async def add(self, department: SDepartment) -> SDepartment:
        department_dict = department.model_dump()
        async with unit_of_work() as uow:
            repository: DepartmentRepository = self.repository_factory(uow.session)
            department_exist = await repository.get_one_by_filter(
                {"department_name": department.department_name}
            )
            if department_exist:
                raise AlreadyExistException(
                    f"Департамент с названием {department.department_name} уже существует"
                )
            new_department = await repository.add(department_dict)
            return new_department


    async def update(self, department_id: int, instance: DepartmentUpdate):
        print(instance)
        department_dict = instance.model_dump()
        async with unit_of_work() as uow:
            repository: DepartmentRepository = self.repository_factory(uow.session)
            department_exist = await repository.get_one_by_filter(department_dict)
            if department_exist:
                raise AlreadyExistException(
                    f"Департамент с названием {instance.department_name} уже существует"
                )
            return await repository.update_by_id(department_id, department_dict)


department_service = DepartmentService(department_repository_factory)
