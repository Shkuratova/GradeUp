from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from api.decorators import check_role, exception_handler
from api.roles import UserRole
from db.uow import unit_of_work
from services.profile import ProfileService
from schemas.users import UserInfo
from schemas.profiles import (
    SProfileAdd,
    SProfileUpdate,
    ProfileList,
)

profile_router = APIRouter(prefix="/profile", tags=["Profiles"])


@profile_router.get("", response_model=list[ProfileList])
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(current_user: UserInfo = Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).get_all()


@profile_router.post("")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(profile: SProfileAdd, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).add_profile(profile)


@profile_router.get("/{profile_id}")
@exception_handler
async def get_by_id(profile_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        return await ProfileService(uow.session).get_with_details(profile_id)

@profile_router.put("/{profile_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update_by_id(profile_id: int, profile: SProfileUpdate, current_user = Depends(get_current_user)):
    async with unit_of_work() as uow:
        await ProfileService(uow.session).update_by_id(profile_id, profile)
    return {"detail": "Профиль успешно обновлен."}



# @profile_router.get("/{profile_id}/levels", response_model=ProfileLevels)
# @check_role([UserRole.ADMIN, UserRole.SPO])
# @exception_handler
# async def get_levels(profile_id: int, current_user=Depends(get_current_user)):
#     async with unit_of_work() as uow:
#         return await ProfileService(uow.session).get_profile_levels(profile_id)

