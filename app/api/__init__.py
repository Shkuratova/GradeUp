from api.admin import admin_router
from api.auth import auth_router
from api.users import (
    user_router,
    user_detail_router,
    user_profile_router,
    user_profile_detail_router,
    user_skill_router,
    evaluation_router,
)
from api.organization import department_router, division_router
from api.profiles import profile_router, skill_router, category_router
from api.meetings import meeting_router

admin_router.include_router(department_router)
admin_router.include_router(division_router)


user_detail_router.include_router(user_profile_detail_router)
user_detail_router.include_router(user_skill_router)
user_router.include_router(user_detail_router)
routers = [
    admin_router,
    auth_router,
    user_profile_router,
    user_router,
    profile_router,
    skill_router,
    evaluation_router,
    meeting_router,
    category_router
]
