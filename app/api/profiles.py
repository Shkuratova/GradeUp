from fastapi import APIRouter, Depends
from services.profile import profile_service, level_service
from schemas.profiles import ProfileAdd, SProfile, LevelAdd, ProfileLevels
from api.decorators import check_role, exception_handler
from dependencies.auth import get_current_user
from api.roles import UserRole
from schemas.users import UserInfo
profile_router = APIRouter(prefix="/profile", tags=["Profiles"])



@profile_router.get("", response_model=list[SProfile])
@check_role([UserRole.ADMIN, UserRole.SPO, UserRole.SUPERVISOR])
@exception_handler
async def get_all(current_user: UserInfo = Depends(get_current_user)):
    if current_user.role_name  == UserRole.SUPERVISOR:
        return await profile_service.get_all_by_department_id(current_user.department_id)
    return await profile_service.get_all()


@profile_router.post("")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(profile: ProfileAdd, current_user=Depends(get_current_user)):
    return await profile_service.add(profile)


@profile_router.get("/{profile_id}")
@exception_handler
async def get_by_id(profile_id: int, current_user=Depends(get_current_user)):
    return await profile_service.get_by_id(profile_id)


@profile_router.post("/{profile_id}/levels")
@exception_handler
async def add_level(profile_id: int, level: LevelAdd, current_user=Depends(get_current_user)):
    return await level_service.add(level)


@profile_router.get("/{profile_id}/levels", response_model=ProfileLevels)
@exception_handler
async def get_levels(profile_id: int, current_user=Depends(get_current_user)):
    return await profile_service.get_profile_levels(profile_id)
