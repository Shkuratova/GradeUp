from fastapi import APIRouter, Depends

from api.decorators import check_role, exception_handler
from db.uow import unit_of_work
from dependencies.auth import get_current_user
from schemas.departments import (
    DepartmentBase,
    DepartmentDetail,
    DepartmentSchema,
    DepartmentAddForm,
    DepartmentUpdateForm,
)
from schemas.users import UserInfo
from services import EventService
from services.access import AccessService
from services.department import DepartmentService
from utils.roles import UserRole

department_router = APIRouter(prefix="/departments", tags=["Departments"])


@department_router.post("/", summary="Создать отдел")
@check_role([UserRole.ADMIN])
@exception_handler
async def add(
    department: DepartmentAddForm, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        instance = await DepartmentService(uow.session).add_with_relations(department)
    return instance


@department_router.get(
    "/", response_model=list[DepartmentSchema], summary="Получить список отделов"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(
    current_user: UserInfo = Depends(get_current_user),
) -> list[DepartmentSchema]:
    async with unit_of_work() as uow:
        return await DepartmentService(uow.session).get_all()



@department_router.get(
    "/profiles",
    response_model=list[DepartmentDetail],
    summary="Получить список отделов с доступными профилями",
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
async def get_all_with_profiles(current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        departments_id = await AccessService(uow.session).get_department_filter(
            current_user
        )
        return await DepartmentService(uow.session).get_all_with_profiles(
            departments_id
        )


@department_router.get(
    "/{department_id}",
    response_model=DepartmentDetail,
    summary="Получить отдел по id с руководителем и списком доступных отделов",
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_department_detail(
    department_id: int, current_user: UserInfo = Depends(get_current_user)
) -> DepartmentBase:
    async with unit_of_work() as uow:
        await AccessService(uow.session).get_department_filter(
            current_user, [department_id]
        )
        return await DepartmentService(uow.session).get_detail(department_id)


@department_router.put(
    "/{department_id}",
    response_model=DepartmentDetail,
    summary="Обновление отдела с руководителем и списком профилей",
)
@check_role([UserRole.ADMIN])
@exception_handler
async def update_by_id(
    department_id: int,
    department: DepartmentUpdateForm,
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        upd, old = await DepartmentService(uow.session).update_with_relations(
            department_id, department
        )

        if department.supervisor_id and upd.supervisor_id != old.supervisor_id:

            await EventService(uow.session).log_set_department_supervisor(
                department=upd, current_user=current_user
            )

        return upd


@department_router.delete("/{department_id}", summary="Удалить отдел по id")
@check_role([UserRole.ADMIN])
@exception_handler
async def delete_by_id(
    department_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await DepartmentService(uow.session).delete(department_id)
    return {"detail": f"Департамент с id = {department_id} удален"}


@department_router.delete(
    "/{department_id}/supervisor", summary="Открепить руководителя от отдела"
)
@check_role([UserRole.ADMIN])
@exception_handler
async def remove_supervisor(department_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        department = await DepartmentService(uow.session).remove_supervisor(
            department_id
        )
        await EventService(uow.session).log_department_supervisor_removed(
            department, current_user
        )
    return {"detail": "Руководитель отдеда откреплён."}
