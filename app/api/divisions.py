from fastapi import APIRouter, Depends

from api.decorators import check_role, exception_handler
from db.uow import unit_of_work
from dependencies.auth import get_current_user
from schemas.departments import (
    DivisionDetail,
    DivisionAddForm,
    DivisionUpdateForm,
    DivisionSchema,
)
from services.department import DivisionService
from utils.roles import UserRole

division_router = APIRouter(prefix="/divisions")

@division_router.get("/", response_model=list[DivisionSchema])
@check_role([UserRole.ADMIN])
@exception_handler
async def get_all(current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).get_all()

@division_router.post("/", response_model=DivisionDetail)
@check_role([UserRole.ADMIN])
@exception_handler
async def add(division: DivisionAddForm, current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).add_with_relations(division)

@division_router.get("/{division_id}", response_model=DivisionDetail)
@exception_handler
async def get_division_detail(division_id: int, current_user= Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).get_division_detail(division_id)


@division_router.put("/{division_id}", response_model=DivisionDetail)
@check_role([UserRole.ADMIN])
@exception_handler
async def update_by_id_with_departments(division_id: int, division: DivisionUpdateForm, current_user= Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).update_division_with_relations(division_id, division)

@division_router.post("/{division_id}/remove-supervisor")
@check_role([UserRole.ADMIN])
@exception_handler
async def remove_supervisor(division_id: int, current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        await DivisionService(uow.session).remove_supervisor(division_id)