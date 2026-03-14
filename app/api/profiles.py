from fastapi import APIRouter, Depends
from services.profile import profile_service as service
from schemas.profiles import ProfileBase, ProfileAdd
from api.decorators import check_role, exception_handler
from dependencies.auth import get_current_user
from api.levels import level_router

profile_router = APIRouter(prefix="/profile", tags=["Profiles"])

profile_router.include_router(level_router)


@profile_router.get("", response_model=list[ProfileBase])
async def get_all():
    return await service.get_all()


@profile_router.post("")
@check_role(["Admin"])
@exception_handler
async def add(profile: ProfileAdd, current_user=Depends(get_current_user)):
    return await service.add_profile(profile)


@profile_router.get("/{profile_id}")
@exception_handler
async def get_by_id(profile_id: int, current_user=Depends(get_current_user)):
    return await service.get_by_id(profile_id)


@profile_router.get("/{profile_id}/levels")
@exception_handler
async def get_levels(profile_id: int, current_user=Depends(get_current_user)):
    return await service.get_profile_levels(profile_id)
