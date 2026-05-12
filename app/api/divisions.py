from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from schemas.users import UserInfo
from utils.roles import UserRole
from api.decorators import check_role, exception_handler
from db.uow import unit_of_work
from services.department import DivisionService
from schemas.departments import DepartmentBase, DepartmentAdd, DepartmentUpdate, DivisionAdd, DivisionUpdate, \
    DivisionDetail

division_router = APIRouter(prefix="/divisions")

@division_router.get("/")
@check_role([UserRole.ADMIN])
@exception_handler
async def get_all(current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).get_all()

@division_router.post("/")
@check_role([UserRole.ADMIN])
@exception_handler
async def add(division: DivisionAdd, current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).add(division)

@division_router.get("/{division_id}", response_model=DivisionDetail)
@exception_handler
async def get_division_detail(division_id: int, division: DivisionUpdate, current_user= Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).get_division_detail(division_id)



@division_router.put("/{division_id}", response_model=DivisionDetail)
@check_role([UserRole.ADMIN])
@exception_handler
async def update_by_id_with_departments(division_id: int, division: DivisionUpdate, current_user= Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).update_division_with_relations(division_id, division)

