from contextlib import ExitStack, asynccontextmanager
import typing
import pytest
from fastapi.testclient import TestClient

from sql_app.database import get_db, session_manager
# from sql_app import *
from app import init_app


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

@pytest.fixture(autouse=True)
async def creat_tables(connection_test):
    connection = session_manager.connect() 
    await session_manager.drop_db_and_tables(connection)
    await session_manager.create_db_and_tables(connection)


@pytest.fixture(autouse=True)
async def session_override(app, connection_test):
    async def get_db_override():
        yield session_manager.session()

    app.dependency_overrides[get_db] = get_db_override

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



