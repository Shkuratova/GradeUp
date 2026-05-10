from api.admin import admin_router
from api.auth import auth_router
from api.user import router as user_router
from api.department import department_router
from api.profiles import profile_router
from api.skill import skill_router
from api.categories import category_router
from api.stages import stage_router
from api.user_profiles import user_profile_router

skill_router.include_router(stage_router)

routers = [
    admin_router,
    auth_router,
    user_router,
    department_router,
    profile_router,
    skill_router,
    user_profile_router,
    category_router,
]