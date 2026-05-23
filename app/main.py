from fastapi import FastAPI
from api import routers
from core.config import settings
from core.log import setup_logging


def create_app() -> FastAPI:
    setup_logging(debug=settings.debug)


    app = FastAPI(title=settings.app_name, debug=settings.debug)

    for router in routers:
        app.include_router(router)


    return app


app = create_app()

@app.get("/")
def check():
    return {"msg": "OK"}
