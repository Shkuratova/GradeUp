from sqlalchemy.ext.asyncio import AsyncSession

from db.repository import UserRepository, DivisionRepository, DepartmentRepository
from exceptions.common import NotFoundException, DataValidationError, ConflictException
from schemas.departments import (
    DivisionUpdate,
    DivisionAdd,
    DivisionAddForm,
    DivisionUpdateForm,
    DivisionDetail,
    DivisionBase,
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
        division = await self.repository.get_division_detail(division_id)
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

            user: UserInfo = await self.user_repository.get_user_info(
                user_id=division.supervisor_id
            )
            if (
                user.managed_division is not None
                and user.managed_division.id != division_id
                or user.managed_department_id is not None
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
        upd = await self.get_division_detail(division_id)
        return upd, old

    async def remove_supervisor(self, division_id):
        division = await self.get_division_detail(division_id)
        if division.supervisor_id is None:
            raise ConflictException("У направления нет руководителя.")
        await self.repository.update_by_id(division_id, {"supervisor_id": None})
        return division

    async def delete(self, division_id):
        division = await self.get_by_id(division_id)
        if division.supervisor_id:
            raise ConflictException(
                "Нельзя удалить направление с назначенным руководителем."
            )
        department_cnt = await self.repository.get_department_cnt(division_id)
        if department_cnt:
            raise ConflictException(
                f"Нельзя удалить направление с подчиненными отделами (Отделов в направлении: {department_cnt})"
            )
        await self.repository.delete_by_id(division_id)

    async def get_with_departments(self, division_id: int | None = None):
        if division_id:
            res = await self.repository.get_division_detail(division_id)
            return [res]
        return await self.repository.get_with_departments()
