from fastapi import APIRouter, Depends
from dependencies import get_current_user
from api.decorators import exception_handler, check_role
from utils.roles import UserRole
from db.repository import RoleRepository
from db.uow import unit_of_work

from schemas.users import (
    UserInfo,
     SRole
)


admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@admin_router.get("/roles", response_model=list[SRole])
@check_role([UserRole.ADMIN])
@exception_handler
async def get_all(current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        roles = await RoleRepository(uow.session).get_all()
        return roles

