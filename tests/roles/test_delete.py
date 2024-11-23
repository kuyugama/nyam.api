from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, role_user, master_key):
    response = await requests.roles.delete_role(client, master_key, role_user.name)
    print(response.json())
    assert response.status_code == 200


async def test_has_users(client, role_user, user_regular, master_key):
    response = await requests.roles.delete_role(client, master_key, role_user.name)
    print(response.json())
    assert response.status_code == 400

    assert_contain(
        response.json(),
        category="roles",
        code="role-has-users",
    )


async def test_fallback_to_default(client, role_user, user_regular, role_unverified, master_key):
    response = await requests.roles.delete_role(client, master_key, role_user.name)
    print("Delete role:", response.json())
    assert response.status_code == 200

    response = await requests.users.user(client, user_regular.nickname)
    print("Get user:", response.json())
    assert response.status_code == 200

    assert response.json()["role"]["name"] == role_unverified.name


async def test_replacement(client, role_admin, user_admin, role_user, master_key):
    response = await requests.roles.delete_role(client, master_key, role_admin.name, role_user.name)
    print("Delete role:", response.json())
    assert response.status_code == 200

    response = await requests.users.user(client, user_admin.nickname)
    print("Get user:", response.json())
    assert response.status_code == 200
    assert response.json()["role"]["name"] == role_user.name
