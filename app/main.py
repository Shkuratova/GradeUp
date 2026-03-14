from fastapi import FastAPI
from api import auth_router, user_router, department_router, profile_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(department_router)
app.include_router(profile_router)


@app.get("/")
def check():
    return {"msg": "OK"}



