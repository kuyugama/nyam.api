from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, role_unverified):
    response = await requests.roles.list_roles(client)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "page": 1, "pages": 1}

    role = response.json()["items"][0]
    assert_contain(
        role,
        title=role_unverified.title,
        permissions=role_unverified.permissions,
        default=role_unverified.default,
        name=role_unverified.name,
        id=role_unverified.id,
    )


async def test_no_roles(client):
    response = await requests.roles.list_roles(client)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["pagination"] == {"total": 0, "page": 1, "pages": 0}
