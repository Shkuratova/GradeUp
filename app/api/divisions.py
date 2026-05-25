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
from schemas.users import UserInfo
from services import EventService, AccessService
from services.department import DivisionService
from utils.roles import UserRole

division_router = APIRouter(prefix="/divisions", tags=["Divisions"])


@division_router.get(
    "/", response_model=list[DivisionSchema], summary="Получить список направлений"
)
@check_role([UserRole.ADMIN])
@exception_handler
async def get_all(current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).get_all()

@division_router.get(
    "/departments",
    response_model=list[DivisionDetail],
    summary="Получить список направлений с отделами"
)
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_division_departments(current_user= Depends(get_current_user)):
    async with unit_of_work() as uow:
        division_id = await AccessService.get_managed_division(current_user)
        return await DivisionService(uow.session).get_with_departments(division_id)

@division_router.post("/", response_model=DivisionDetail, summary="Создать направление")
@check_role([UserRole.ADMIN])
@exception_handler
async def add(division: DivisionAddForm, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await DivisionService(uow.session).add_with_relations(division)


@division_router.get(
    "/{division_id}",
    response_model=DivisionDetail,
    summary="Получить направление по id с руководителем и подчиненными отделами",
)
@exception_handler
async def get_division_detail(division_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await AccessService.can_get_division(division_id, current_user)
        return await DivisionService(uow.session).get_division_detail(division_id)


@division_router.put(
    "/{division_id}",
    response_model=DivisionDetail,
    summary="Обновить направление со списком подчиненных отделов и руководителем",
)
@check_role([UserRole.ADMIN])
@exception_handler
async def update_by_id_with_departments(
    division_id: int,
    division: DivisionUpdateForm,
    current_user: UserInfo = Depends(get_current_user),
):
    async with unit_of_work() as uow:
        upd, old = await DivisionService(uow.session).update_with_relations(
            division_id, division
        )

        if division.supervisor_id and upd.supervisor_id != old.supervisor_id:

            await EventService(uow.session).log_set_division_supervisor(
                division=upd, current_user=current_user
            )

        return upd


@division_router.delete("/{division_id}", summary="Удалить направление по id")
@check_role([UserRole.ADMIN])
@exception_handler
async def delete(division_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await DivisionService(uow.session).delete(division_id)
        return {"detail": f"Направление с id={division_id} удалено."}


@division_router.delete(
    "/{division_id}/supervisor", summary="Открепить руководителя от направления"
)
@check_role([UserRole.ADMIN])
@exception_handler
async def remove_supervisor(
    division_id: int, current_user: UserInfo = Depends(get_current_user)
):
    async with unit_of_work() as uow:
        division = await DivisionService(uow.session).remove_supervisor(division_id)
        await EventService(uow.session).log_remove_division_supervisor(
            division, current_user
        )
        return {"detail": "Руководитель направления откреплён."}
