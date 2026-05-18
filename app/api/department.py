from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from schemas.users import UserInfo
from utils.roles import UserRole
from api.decorators import check_role, exception_handler
from db.uow import unit_of_work
from services.department import DepartmentService
from schemas.departments import (
    DepartmentBase,
    DepartmentAdd,
    DepartmentUpdate,
    DepartmentDetail,
)

department_router = APIRouter(prefix="/departments", tags=["Departments"])


@department_router.post("/")
@check_role([UserRole.ADMIN])
@exception_handler
async def add(
    department: DepartmentAdd, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        instance = await DepartmentService(uow.session).add(department)
    return instance


@department_router.get("/")
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(
    current_user: UserInfo = Depends(get_current_user),
) -> list[DepartmentBase]:
    async with unit_of_work() as uow:
        return await DepartmentService(uow.session).get_all()


@department_router.get("/{department_id}", response_model=DepartmentDetail)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_department_detail(
    department_id: int, current_user: UserInfo = Depends(get_current_user)
) -> DepartmentBase:
    async with unit_of_work() as uow:
        return await DepartmentService(uow.session).get_detail(department_id)


@department_router.put("/{department_id}", response_model=DepartmentDetail)
@check_role([UserRole.ADMIN])
@exception_handler
async def update_by_id(
    department_id: int,
    department: DepartmentUpdate,
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        return await DepartmentService(uow.session).update_department_with_relations(
            department_id, department
        )


@department_router.delete("/{department_id}")
@check_role([UserRole.ADMIN])
@exception_handler
async def delete_by_id(
    department_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        await DepartmentService(uow.session).delete_by_id(department_id)
    return {"detail": f"Департамент с id = {department_id} удален"}
