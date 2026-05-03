from fastapi import FastAPI
from api import routers

app = FastAPI()

for router in routers:
    app.include_router(router)

@app.get("/")
def check():
    return {"msg": "OK"}
