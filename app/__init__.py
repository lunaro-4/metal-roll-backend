from contextlib import asynccontextmanager
from sql_app.database import session_manager
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_path : str = '/sql_app.db'
    date_format : str = "%Y-%m-%d"
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

def init_app(prod_db = True):
    db = "sqlite+aiosqlite://" + settings.database_path

    lifespan = None

    if prod_db:
        session_manager.init(db)

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

