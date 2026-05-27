from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from api.decorators import check_role, exception_handler
from utils.roles import UserRole
from db.uow import unit_of_work
from services import CategoryService, SkillCategoryService
from schemas.categories import CategoryBase, CategoryAdd, SkillCategory

category_router = APIRouter(prefix="/category", tags=["Categories"])


@category_router.post(
    "/", response_model=CategoryBase, summary="Создать категорию навыков"
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add(category: CategoryAdd, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        instance = await CategoryService(uow.session).add(category)
    return instance


@category_router.get(
    "/", response_model=list[CategoryBase], summary="Получить список категорий навыков"
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_all(current_user=Depends(get_current_user)) -> list[CategoryBase]:
    async with unit_of_work() as uow:
        return await CategoryService(uow.session).get_all()


@category_router.post(
    "/skills", response_model=CategoryBase, summary="Прикрепить навык к категории"
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def add_skill_category(
    category_skill: SkillCategory, current_user=Depends(get_current_user)
):
    async with unit_of_work() as uow:
        res = await SkillCategoryService(uow.session).add(category_skill)
        return res


@category_router.get(
    "/{category_id}", response_model=CategoryBase, summary="Получить категорию по id"
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def get_by_id(
    category_id: int, current_user=Depends(get_current_user)
) -> CategoryBase:
    async with unit_of_work() as uow:
        return await CategoryService(uow.session).get_by_id(category_id)


@category_router.post(
    "/{category_id}", response_model=CategoryBase, summary="Изменить название категории"
)
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def update_by_id(
    category_id: int,
    category: CategoryAdd,
    current_user=Depends(get_current_user),
):
    async with unit_of_work() as uow:
        return await CategoryService(uow.session).update_by_id(category_id, category)


@category_router.delete("/{category_id}", summary="Удалить категорию по id")
@check_role([UserRole.ADMIN, UserRole.SPO])
@exception_handler
async def delete_by_id(category_id: int, current_user=Depends(get_current_user)):
    async with unit_of_work() as uow:
        await CategoryService(uow.session).delete_by_id(category_id)
    return {"detail": f"Категория с id = {category_id} удален"}
