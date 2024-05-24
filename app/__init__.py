from contextlib import asynccontextmanager
from sql_app.database import sessionmaker

from fastapi import FastAPI

def init_app(prod_db = True):
    lifespan = None

    if prod_db:
        sessionmaker.init()

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmaker.engine is not None:
                await sessionmaker.close()

    app = FastAPI(lifespan=lifespan)


    from .main import router

    app.include_router(router)

    return app

# app = init_app()
