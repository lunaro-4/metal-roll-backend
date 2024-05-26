from contextlib import ExitStack, asynccontextmanager
import typing
import pytest
import asyncio
from fastapi.testclient import TestClient

from sql_app.database import get_db, session_manager
from app import init_app


# tests can't find app, and does not work anyway, so I gave up (

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite://./test_sql.db"


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield init_app(prod_db = False)

@pytest.fixture
def client(app):
    yield TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def connection_test():
    session_manager.init(SQLALCHEMY_DATABASE_URL)
    yield
    await session_manager.close()




@pytest.fixture(scope="function", autouse=True)
async def session_override(app, connection_test):
    async def get_db_override():
        yield session_manager.session()
    app.dependency_overrides[get_db] = get_db_override

@pytest.fixture(scope="function", autouse=True)
async def create_tables(connection_test, session_manager):
    connection = session_manager.connect() 
    await session_manager.drop_db_and_tables(connection)
    await session_manager.create_db_and_tables(connection)

