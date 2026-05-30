from sqlalchemy.ext.asyncio import AsyncSession

from db.models.types import DepartmentRole
from db.repository import (
    UserRepository,
    DepartmentRepository,
    DepartmentProfileRepository,
)
from db.repository.organization import DepartmentUserRepository
from exceptions.common import NotFoundException, DataValidationError, ConflictException
from schemas.departments import (
    DepartmentUpdate,
    DepartmentAdd,
    DepartmentDetail,
    DepartmentAddForm,
    DepartmentUpdateForm,
    DepartmentBase,
)
from schemas.users import UserInfo
from services.base import BaseService


class DepartmentService(BaseService):
    entity_name = "Отдел"
    unique_fields = ["department_name"]

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.repository = DepartmentRepository(session)
        self.user_repository = UserRepository(session)
        self.department_profile_repository = DepartmentProfileRepository(session)
        self.department_user_repository = DepartmentUserRepository(session)

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

    async def set_supervisor(self, user_id: int, department_id: int, old_supervisor: int | None = None):

        if old_supervisor is not None and old_supervisor != user_id:
            raise ConflictException("Отделу уже назначен руководитель")
        if old_supervisor == user_id:
            return 
        user = await self.user_repository.get_user_info(user_id=user_id)
        user = UserInfo.model_validate(user, from_attributes=True)

        if user is None:
            raise NotFoundException(f"Пользователь с id={user_id} не найден")
        if (
            user.is_department_supervisor()
            and user.department_id != department_id
            or user.is_division_supervisor()
        ):
            raise DataValidationError(
                "Сотрудник может быть руководителем только внутри одного направления или отдела"
            )
        if user.department_id != department_id:
            raise DataValidationError(
                "Руководителем может быть назначен только сотрудник из выбранного отдела."
            )

        if user.department_id is None:
            await self.department_user_repository.add(
                {
                    "user_id": user_id,
                    "department_id": department_id,
                    "role": DepartmentRole.SUPERVISOR
                }
            )
        else:
            await self.department_user_repository.update_by_user_id(
                user_id, {"role": DepartmentRole.SUPERVISOR}
            )

    async def add_with_relations(self, department: DepartmentAddForm):

        new_department = DepartmentAdd(
            department_name=department.department_name,
            description=department.description,
        )
        new_department = await self.add(new_department)
        if department.supervisor_id:
            await self.set_supervisor(department.supervisor_id, new_department.id)

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
        old = await self.get_detail(department_id)
        old = DepartmentDetail.model_validate(old, from_attributes=True)

        if department.supervisor_id:
            await self.set_supervisor(department.supervisor_id, department_id, old.supervisor_id)

        await self.update_by_id(
            department_id,
            DepartmentUpdate(
                department_name=department.department_name,
                description=department.description,
            ),
        )

        if department.profiles is not None:
            old_profiles = old.profiles if old.profiles is not None else []
            old_profiles = set(p.id for p in old_profiles)
            new_profiles = set(department.profiles)
            if del_id := old_profiles - new_profiles:
                await self.department_profile_repository.delete_by_profile_id(list(del_id))
            if add_id := new_profiles - old_profiles:
                await self.department_profile_repository.add_list(
                    [{"department_id": department_id, "profile_id": p} for p in add_id]
                )
            # new_profiles = set(department.profiles)
            # exist_profiles = {p.profile_id: p.id for p in profiles}
            # exist_ids = set(exist_profiles.keys())
            # if del_profiles := [exist_profiles[p] for p in exist_ids - new_profiles]:
            #     await self.department_profile_repository.delete_list(del_profiles)
            # if add_profiles := new_profiles - exist_ids:
            #     await self.department_profile_repository.add_list(
            #         [
            #             {"department_id": department_id, "profile_id": p}
            #             for p in add_profiles
            #         ]
            #     )

        upd = await self.get_detail(department_id)
        return upd, old

    async def remove_supervisor(self, department_id):
        department = await self.get_detail(department_id)
        if department.supervisor_id is None:
            raise ConflictException("У отдела нет руководителя.")
        await self.department_user_repository.update_by_user_id(
            department.supervisor_id, {"role": DepartmentRole.EMPLOYEE}
        )
        return DepartmentDetail.model_validate(department, from_attributes=True)

    async def delete(self, department_id):
        department = await self.get_detail(department_id)
        if department.supervisor_id is not None:
            raise ConflictException(
                "Нельзя удалить профиль с назначенным руководителем"
            )
        res = await self.department_user_repository.get_user_count(department_id)
        if res:
            raise ConflictException(
                f"Нельзя удалить отдел с сотрудниками (Сотрудников в отделе: {res})"
            )
        await self.repository.delete_by_id(department_id)

    async def get_list(self, departments_id: list[int] | None = None):
        return await self.repository.get_by_ids(departments_id)
