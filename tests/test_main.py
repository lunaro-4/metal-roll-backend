import pytest
import asyncio


pytest_plugins = ('pytest_asyncio')

@pytest.mark.asyncio
async def test_read_main(client, create_tables):
    response = client.get("/")
    assert response.status_code == 200

    post_request = { "weight" : 12, "length" : 13, "add_date" : None, "del_date" : None }
    response = client.post("/coil", json=post_request)
    
    assert response.status_code == 200
    response.url
    post_request = { "id" : 1, "weight" : 12, "length" : 13, "add_date" : None, "del_date" : None }
    assert response.json() == post_request
