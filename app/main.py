from fastapi import FastAPI
from api import routers
from config import settings

app = FastAPI()


for router in routers:
    app.include_router(router)

@app.get("/")
def check():
    return {"msg": "OK"}
