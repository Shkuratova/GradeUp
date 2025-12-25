from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user, check_role_id
from app.db import db_helper
from app.profiles.schemas import SProfile, SProfileFilter, SSkillInfo
from app.profiles.dao import ProfileDAO, SkillDAO


router = APIRouter(
    prefix="/profiles",
    tags=["Edit profiles"],
    dependencies=[Depends(check_role_id([3, 4]))],
)


@router.get("/")
async def get_all_profiles(
    position: Annotated[SProfileFilter, Query()],
    session: AsyncSession = Depends(db_helper.session_without_commit),
) -> list[SProfile]:
    res = await ProfileDAO(session=session).get_profiles_with_positions(position)
    return list(res)


@router.get("/skills")
async def get_all_skills(
    session: AsyncSession = Depends(db_helper.session_without_commit)
) -> list[SSkillInfo]:
    res = await SkillDAO(session=session).get_skills_with_full_info()
    print('\n\n fdghsrthr ',list(res))
    return list(res)
    