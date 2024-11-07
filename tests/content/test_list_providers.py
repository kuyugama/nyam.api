from tests import requests


async def test_normal(client):
    response = await requests.content.list_providers(client)
    print(response.json())
    assert response.status_code == 200

    for provider in response.json():
        assert "name" in provider
        assert "description" in provider
        assert "identifier" in provider
