from tests import requests


async def test_normal(client, role_unverified):
    response = await requests.roles.list_roles(client)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "page": 1, "pages": 1}

    role = response.json()["items"][0]
    assert role["description"] == role_unverified.title
    assert role["permissions"] == role_unverified.permissions
    assert role["default"] == role_unverified.default
    assert role["name"] == role_unverified.name
    assert role["id"] == role_unverified.id


async def test_no_roles(client):
    response = await requests.roles.list_roles(client)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["pagination"] == {"total": 0, "page": 1, "pages": 0}
