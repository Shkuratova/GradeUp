from api.auth import auth_router
from api.user import router as user_router
from api.department import department_router
from api.profiles import profile_router
from api.skill import skill_router
from api.questions import question_router
from api.categories import category_router

routers = [
    auth_router,
    user_router,
    department_router,
    profile_router,
    skill_router,
    question_router,
    category_router,
]