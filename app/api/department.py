from fastapi import APIRouter, Depends, HTTPException
from services.department import department_service as service
from schemas.departments import SDepartment, DepartmentAdd, DepartmentUpdate
from api.decorators import check_role, exception_handler
from dependencies.auth import get_current_user
from api.roles import UserRole
department_router = APIRouter(prefix="/departments", tags=["Departments"])


@department_router.post("/")
@check_role([UserRole.ADMIN])
@exception_handler
async def add(department: DepartmentAdd, current_user=Depends(get_current_user)):
    instance = await service.add(department)
    return instance


@department_router.get("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(current_user=Depends(get_current_user)) -> list[SDepartment]:
    return await service.get_all()


@department_router.get("/{department_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_by_id(
    department_id: int, current_user=Depends(get_current_user)
) -> SDepartment:
    return await service.get_by_id(department_id)


@department_router.post("/{department_id}")
@check_role([UserRole.ADMIN])
@exception_handler
async def update_by_id(
    department_id: int,
    department: DepartmentUpdate,
    current_user=Depends(get_current_user),
):
    await service.update_by_id(department_id, department)
    return {"detail": "Департамент успешно обновлен"}


@department_router.delete("/{department_id}")
@check_role([UserRole.ADMIN])
@exception_handler
async def delete_by_id(department_id: int, current_user=Depends(get_current_user)):
    await service.delete_by_id(department_id)
    return {"detail": f"Департамент с id = {department_id} удален"}
