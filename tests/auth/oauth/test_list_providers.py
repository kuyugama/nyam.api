from tests import requests


async def test_normal(client):
    response = await requests.auth.list_oauth_providers(client)
    print(response.json())
    assert response.status_code == 200

    assert isinstance(response.json(), list)
