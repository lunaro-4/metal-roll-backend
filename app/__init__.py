from contextlib import asynccontextmanager
from sql_app.database import session_manager

from fastapi import FastAPI

def init_app(prod_db = True):
    lifespan = None

    if prod_db:
        session_manager.init()

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await session_manager.create_db_and_tables()
            yield
            if session_manager.engine is not None:
                await session_manager.close()

    app = FastAPI(lifespan=lifespan)


    from .views import router

    app.include_router(router)

    return app

# app = init_app()
