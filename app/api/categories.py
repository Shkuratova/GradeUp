from fastapi import APIRouter, Depends, Query
from services.skill import CategoryService, SkillCategoryService
from db.uow import unit_of_work
from schemas.categories import CategoryBase, CategoryAdd, SkillCategory
from api.decorators import check_role, exception_handler
from dependencies.auth import get_current_user
from api.roles import UserRole


category_router = APIRouter(prefix="/category",  tags=["Categories"])

@category_router.post("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(category: CategoryAdd, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        instance = await CategoryService(uow.session).add(category)
    return instance


@category_router.get("/")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(current_user=Depends(get_current_user)) -> list[CategoryBase]:
    async with unit_of_work() as uow:
        return await CategoryService(uow.session).get_all()


@category_router.post("/skills")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add_skill_category(category_skill: SkillCategory, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        res = await SkillCategoryService(uow.session).add(category_skill)
        return res



@category_router.get("/{category_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_by_id(
    category_id: int, current_user=Depends(get_current_user)
) -> CategoryBase:
    async with unit_of_work() as uow:
        return await CategoryService(uow.session).get_by_id(category_id)


@category_router.post("/{category_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update_by_id(
    category_id: int,
    category: CategoryAdd,
    current_user=Depends(get_current_user),
):
    async with unit_of_work() as uow:
        await CategoryService(uow.session).update_by_id(category_id, category)
    return {"detail": "Категория успешно обновлена"}


@category_router.delete("/{category_id}")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def delete_by_id(category_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await CategoryService(uow.session).delete_by_id(category_id)
    return {"detail": f"Категория с id = {category_id} удален"}


