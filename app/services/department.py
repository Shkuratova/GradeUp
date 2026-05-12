from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import UserRepository, ProfileRepository, DepartmentProfileRepository
from db.repository.department import DepartmentRepository, DivisionRepository
from exceptions.common import NotFoundException
from exceptions.user import ForbiddenException
from schemas.departments import (
    DivisionUpdate,
    DivisionAdd,
    DepartmentUpdate,
    DepartmentAdd, DepartmentDetail,
)
from schemas.users import UserInfo
from services.base import BaseService
from utils.roles import UserRole


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
            if not await self.repository.get_by_id(division_id):
                raise NotFoundException(f"Направление с id = {division_id} не найдено.")
            if division.division_name:
                new_division = DivisionAdd(division_name=division.division_name)
                new_division = await self.update_by_id(division_id, new_division)
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
        if not await self.repository.exists({"id": department_id}):
            raise NotFoundException(f"Отдел с id ={department_id} не найден.")

        if department.department_name is not None:
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
            new_profiles = set(department.profiles)
            exist_profiles = {p.profile_id: p.id for p in profiles}
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
        return DepartmentDetail.model_validate(new_department, from_attributes=True)

    async def get_accessible_departments(self, current_user: UserInfo, department_id: int | None = None):

        if current_user.role_name == UserRole.EMPLOYEE:
            raise ForbiddenException("Отказано в доступе.")

        if current_user.role_name in [UserRole.ADMIN, UserRole.SPO]:
            return [department_id] if department_id else None

        if current_user.division_id is not None:
            departments = await self.repository.get_ids_by_division_id(current_user.division_id)
            if not departments:
                raise ForbiddenException("Нет доступных отделов в вашем подразделении.")

            if department_id:
                if department_id not in departments:
                    raise ForbiddenException("Нет доступа к выбранному отделу.")
                return [department_id]
            return departments

        if current_user.department_id:
            if department_id and department_id != current_user.department_id:
                raise ForbiddenException("Нет доступа к выбранному отделу.")
            return [current_user.department_id]

        raise ForbiddenException("Руководитель должен быть привязан к отделу или подразделению.")

