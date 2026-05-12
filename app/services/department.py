from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import UserRepository, ProfileRepository, DepartmentProfileRepository
from db.repository.department import DepartmentRepository, DivisionRepository
from exceptions.common import NotFoundException
from schemas.departments import (
    DivisionUpdate,
    DivisionAdd,
    DepartmentUpdate,
    DepartmentAdd, DepartmentDetail,
)
from services.base import BaseService


class DivisionService(BaseService):
    entity_name = "Направление"
    unique_fields = ["division_name"]
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = DivisionRepository(session)
        self.department_repository = DepartmentRepository(session)
        self.user_repository = UserRepository(session)

    async def get_division_detail(self, division_id: int):
            return await self.repository.get_division_detail(division_id)

    async def update_division_with_relations(self, division_id: int, division: DivisionUpdate):
            new_division = DivisionAdd(division_name=division.division_name)
            new_division = await self.update_by_id(division_id, new_division)
            if not new_division:
                raise NotFoundException(f"Направление с id = {division_id} не найдено.")
            for department_id in division.departments:
                await self.department_repository.update_by_id(department_id, {"division_id": division_id})
            if division.supervisor_id:
                await self.user_repository.update_by_id(division.supervisor_id, {"managed_division_id": division_id})

            return await self.get_division_detail(division_id)


class DepartmentService(BaseService):
    entity_name = "Отдел"
    unique_fields = ["department_name"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = DepartmentRepository(session)
        self.user_repository = UserRepository(session)
        self.department_profile_repository = DepartmentProfileRepository(session)

    async def get_detail(self, department_id):
        department = await self.repository.get_detail(department_id)
        if department is None:
            raise NotFoundException(f"Отдел с id ={department_id} не найден.")
        return department

    async def update_department_with_relations(self, department_id: int, department: DepartmentUpdate):
        print("FDFFDD")
        if not await self.repository.exists({"id": department_id}):
            raise NotFoundException(f"Отдел с id ={department_id} не найден.")

        if department.department_name is not None:
            print("DEAPRTMENT_PROFILES1", department.department_name)
            await self.update_by_id(
                department_id, DepartmentAdd(department_name=department.department_name)
            )

        if user_id := department.supervisor_id:
            await self.user_repository.update_by_id(
                user_id, {"managed_department_id": department_id}
            )

        if department.profiles:
            profiles = await self.department_profile_repository.get_all(
                {"department_id": department_id}
            )
            print("DEAPRTMENT_PROFILES1", profiles)
            print("DEAPRTMENT_PROFILES", department.profiles)
            new_profiles = set(department.profiles)
            exist_profiles = {p.profile_id: p.id for p in profiles}
            print("DEAPRTMENT_PROFILES", exist_profiles)
            exist_ids = set(exist_profiles.keys())
            if del_profiles := [
                exist_profiles[p] for p in exist_ids - new_profiles
            ]:
                await self.department_profile_repository.delete_list(del_profiles)
            if add_profiles := new_profiles - exist_ids:
                await self.department_profile_repository.add_list([
                    {'department_id': department_id, 'profile_id': p}
                    for p in add_profiles
                ])

        new_department =  await self.get_detail(department_id)
        print(new_department.profiles[0].__dict__)
        return DepartmentDetail.model_validate(new_department, from_attributes=True)
