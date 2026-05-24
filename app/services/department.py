from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import UserRepository, DepartmentProfileRepository
from db.repository.department import DepartmentRepository, DivisionRepository
from exceptions.common import NotFoundException, DataValidationError, ConflictException
from schemas.departments import (
    DivisionUpdate,
    DivisionAdd,
    DepartmentUpdate,
    DepartmentAdd,
    DepartmentDetail,
    DivisionAddForm,
    DepartmentAddForm,
    DivisionUpdateForm,
    DepartmentUpdateForm,
    DivisionDetail,
    DivisionBase, DepartmentBase,
)
from schemas.users import UserInfo
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
        division =  await self.repository.get_division_detail(division_id)
        return DivisionDetail.model_validate(division)

    async def _update_relations(
        self,
        division_id: int,
        departments: list[int],
    ):
        for department_id in departments:
            await self.department_repository.update_by_id(
                department_id, {"division_id": division_id}
            )

    async def add_with_relations(self, division: DivisionAddForm):
        new_division = DivisionAdd.model_validate(division, from_attributes=True)
        new_division = await self.add(new_division)
        if division.departments:
            await self._update_relations(new_division.id, division.departments)
        return await self.get_division_detail(new_division.id)

    async def update_with_relations(
        self, division_id: int, division: DivisionUpdateForm
    ):

        old = await self.repository.get_by_id(division_id)
        if old is None:
            raise NotFoundException(f"Направление с id = {division_id} не найдено.")
        old = DivisionBase.model_validate(old)
        if division.supervisor_id and division.supervisor_id != old.supervisor_id:

            user: UserInfo = await self.user_repository.get_user_role(
                {"id": division.supervisor_id}
            )
            if (
                user.managed_division is not None
                and user.managed_division.id != division_id
                or user.managed_department is not None
            ):
                raise DataValidationError(
                    "Сотрудник может быть руководителем только внутри одного направления или отдела"
                )
            await self.user_repository.update_by_id(user.id, {"department_id": None})

        new_division = DivisionUpdate(
            division_name=division.division_name,
            description=division.description,
            supervisor_id=division.supervisor_id,
        )
        await self.update_by_id(division_id, new_division)
        if division.departments:
            await self._update_relations(division_id, division.departments)
        upd =  await self.get_division_detail(division_id)
        return upd, old

    async def remove_supervisor(self, division_id):
        division = await self.get_division_detail(division_id)
        if division.supervisor_id is None:
            raise ConflictException("У направления нет руководителя.")
        await self.repository.update_by_id(division_id, {'supervisor_id': None})
        return division

    async def delete(self, division_id):
        division = await self.get_by_id(division_id)
        if division.supervisor_id:
            raise ConflictException("Нельзя удалить направление с назначенным руководителем.")
        department_cnt = await self.repository.get_department_cnt(division_id)
        if department_cnt:
            raise ConflictException(f"Нельзя удалить направление с подчиненными отделами (Отделов в направлении: {department_cnt})")
        await self.repository.delete_by_id(division_id)

    async def get_with_departments(self):
        return await self.repository.get_with_departments()


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
        return DepartmentDetail.model_validate(department, from_attributes=True)

    async def get_all_with_profiles(self, departments_id: list[int] | None = None):
        departments = await self.repository.get_with_profiles(departments_id)
        return departments

    async def get_id_by_division(self, division_id: int):
        return await self.repository.get_id_by_division_id(division_id)

    async def add_with_relations(self, department: DepartmentAddForm):

        new_department = DepartmentAdd(
            department_name=department.department_name,
            description=department.description,
            supervisor_id=department.supervisor_id,
        )
        new_department = await self.add(new_department)
        if department.profiles:
            await self.department_profile_repository.add_list(
                [
                    {"department_id": new_department.id, "profile_id": p}
                    for p in department.profiles
                ]
            )
        return await self.get_detail(new_department.id)

    async def update_with_relations(
        self, department_id: int, department: DepartmentUpdateForm
    ):
        old = await self.get_by_id(department_id)
        old = DepartmentBase.model_validate(old, from_attributes=True)

        if department.supervisor_id:
            user: UserInfo = await self.user_repository.get_user_role(
                {"id": department.supervisor_id}
            )
            if (
                user.managed_department is not None
                and user.managed_department.id != department_id
                or user.managed_division is not None
            ):
                raise DataValidationError(
                    "Сотрудник может быть руководителем только внутри одного направления или отдела"
                )
            if user.department_id != department_id:
                raise DataValidationError("Руководителем может быть назначен только сотрудник из выбранного отдела.")

        await self.update_by_id(
            department_id,
            DepartmentUpdate(
                department_name=department.department_name,
                description=department.description,
                supervisor_id=department.supervisor_id,
            ),
        )

        if department.profiles:
            profiles = await self.department_profile_repository.get_all(
                {"department_id": department_id}
            )
            new_profiles = set(department.profiles)
            exist_profiles = {p.profile_id: p.id for p in profiles}
            exist_ids = set(exist_profiles.keys())
            if del_profiles := [exist_profiles[p] for p in exist_ids - new_profiles]:
                await self.department_profile_repository.delete_list(del_profiles)
            if add_profiles := new_profiles - exist_ids:
                await self.department_profile_repository.add_list(
                    [
                        {"department_id": department_id, "profile_id": p}
                        for p in add_profiles
                    ]
                )

        upd = await self.get_detail(department_id)
        return upd, old

    async def remove_supervisor(self, department_id):
        department = await self.get_detail(department_id)
        if department.supervisor_id is None:
            raise ConflictException("У отдела нет руководителя.")
        await self.repository.update_by_id(department_id, {'supervisor_id': None})
        return DepartmentDetail.model_validate(department, from_attributes=True)

    async def delete(self, department_id):
        department = await self.get_by_id(department_id)
        if department.supervisor_id is not None:
            raise ConflictException("Нельзя удалить профиль с назначенным руководителем")
        res = await self.repository.get_user_count(department_id)
        if res:
            raise ConflictException(f"Нельзя удалить отдел с сотрудниками (Сотрудников в отделе: {res})")
        await self.repository.delete_by_id(department_id)

