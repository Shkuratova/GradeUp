from fastapi import APIRouter, Depends, HTTPException
from services.department import department_service as service
from schemas.departments import SDepartment, DepartmentAdd, DepartmentUpdate
from dependencies.auth import check_role
from exceptions.common import AlreadyExistException, NotFoundException


department_router = APIRouter(prefix="/departments", tags=["Departments"])



@department_router.post("/")
async def add(department: DepartmentAdd, admin = Depends(check_role(["Admin"]))):
    try:
        instance = await service.add(department)
    except AlreadyExistException as error:
        raise HTTPException(status_code=400, detail=str(error))
    return  instance


@department_router.get("/")
async def get_all(user = Depends(check_role(["Admin", "Specialist"]))) -> list[SDepartment]:
    return await  service.get_all()


@department_router.get("/{id}")
async def get_by_id(department_id: int) -> SDepartment:
    try:
        return await service.get_by_id(department_id)
    except NotFoundException as error:
        raise HTTPException(status_code=403, detail=str(error))


@department_router.post("/{id}")
async def update_by_id(department_id: int, department: DepartmentUpdate):
    try:
         await service.update(department_id, DepartmentUpdate)
    except AlreadyExistException as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {"detail": "Департамент успешно обновлен"}

@department_router.delete("/{id}")
async def delete_by_id(department_id: int):
    try:
        await service.delete(department_id)
        return {"detail": f"Департамент с id = {department_id} удален"}
    except NotFoundException as error:
        raise HTTPException(status_code=400, detail=str(error))




