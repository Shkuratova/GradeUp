from fastapi import FastAPI
from app.auth.router import router as  auth_router

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
def check():
    return {"msg": "OK"}



