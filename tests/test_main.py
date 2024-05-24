from contextlib import asynccontextmanager
import typing
# import requests
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi.testclient import TestClient
from sql_app.database import create_db_and_tables, get_async_session

from .app.main import app


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///test_sql.db"

Base = declarative_base()

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine)

async def create_db_and_tables_ovvr():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session_ovvr() -> typing.AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# app.dependency_overrides[create_db_and_tables] = create_db_and_tables_ovvr
app.dependency_overrides[get_async_session] = get_async_session_ovvr 

@asynccontextmanager
async def lifespan(app):
    await create_db_and_tables()
    yield


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_post():
    post_request = { "weight" : 12, "length" : 13, "add_date" : None, "del_date" : None }
    response = client.post("/coil", json=post_request)
    
    assert response.status_code == 200
    response.url
    post_request = { "id" : 1, "weight" : 12, "length" : 13, "add_date" : None, "del_date" : None }
    assert response.json() == post_request



