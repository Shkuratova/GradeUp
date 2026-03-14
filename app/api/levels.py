from fastapi import APIRouter, Depends
from services.profile import level_service as service
from schemas.profiles import LevelBase, LevelAdd
from api.decorators import check_role, exception_handler
from dependencies.auth import get_current_user

level_router = APIRouter(prefix="/levels", tags=["Level"])


@level_router.get("", response_model=list[LevelBase])
@check_role(["Admin", "Specialist"])
@exception_handler
async def get_all(current_user=Depends(get_current_user)):
    res = await service.get_all()
    return res


@level_router.post("")
@check_role(["Admin", "Specialist"])
@exception_handler
async def add(level: LevelAdd, current_user=Depends(get_current_user)):
    return await service.add(level)


@level_router.get("/{level_id}")
@check_role(["Admin", "Specialist"])
@exception_handler
async def get_by_id(level_id: int, current_user=Depends(get_current_user)):
    return await service.get_by_id(level_id)


@level_router.delete("/{level_id}")
@check_role(["Admin", "Specialist"])
@exception_handler
async def delete(level_id: int, current_user=Depends(get_current_user)):
    return await service.delete_by_id(level_id)
