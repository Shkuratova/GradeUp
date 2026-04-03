from fastapi import APIRouter, Depends, Query
from services.questions import question_service
from services.skill import skill_service
from api.decorators import exception_handler, check_role
from api.roles import UserRole


question_router = APIRouter(prefix="/questions", tags=["Questions"])

@question_router.get("/", )
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all():
    pass

#list
@question_router.post("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add():
    pass

#list
@question_router.patch("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update():
    pass








