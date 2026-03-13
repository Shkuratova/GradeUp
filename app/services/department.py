from db.repository.department import department_repository_factory, DepartmentRepository
from db.uow import unit_of_work
from exceptions.common import NotFoundException, AlreadyExistException
from schemas.departments import SDepartment, DepartmentUpdate


class DepartmentService:
    def __init__(self, repository_factory):
        self.repository_factory = repository_factory

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

    async def get_all(self):
        async with unit_of_work() as uow:
            repository: DepartmentRepository = self.repository_factory(uow.session)
            return await repository.get_all()

    async def get_by_id(self, department_id):
        async with unit_of_work() as uow:
            repository: DepartmentRepository = self.repository_factory(uow.session)
            department = await repository.get_by_id(department_id)
        if department is None:
            raise NotFoundException(f"Департамент с id = {department_id} не найден")
        return department

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

    async def delete(self, department_id: int):
        async with unit_of_work() as uow:
            repository: DepartmentRepository = self.repository_factory(uow.session)
            res = await repository.delete_by_id(data_id=department_id)
        if not res:
            raise NotFoundException(f"Департамент с id = {department_id} не найден")

department_service = DepartmentService(repository_factory=department_repository_factory)
