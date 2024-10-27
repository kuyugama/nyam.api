from tests import requests


async def test_normal(client, master_key):
    role_name = "name"
    role_description = "description"
    default = True
    permissions_ = {}
    expected_permissions = permissions_
    base_role = None
    response = await requests.roles.create_role(
        client,
        master_key,
        role_name,
        role_description,
        default,
        permissions_,
        base_role,
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["name"] == role_name
    assert response.json()["description"] == role_description
    assert response.json()["default"] == default
    assert response.json()["permissions"] == expected_permissions


async def test_use_base(client, master_key, role_user):
    role_name = "name"
    role_description = "description"
    default = True
    permissions_ = {}
    expected_permissions = role_user.permissions
    base_role = role_user.name
    response = await requests.roles.create_role(
        client,
        master_key,
        role_name,
        role_description,
        default,
        permissions_,
        base_role,
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["name"] == role_name
    assert response.json()["description"] == role_description
    assert response.json()["default"] == default
    assert response.json()["permissions"] == expected_permissions


async def test_no_master(client, master_key):
    role_name = "name"
    role_description = "description"
    default = True
    permissions_ = {}
    response = await requests.roles.create_role(
        client,
        "invalid-" + master_key,
        role_name,
        role_description,
        default,
        permissions_,
        None,
    )
    print(response.json())
    assert response.status_code == 401
    assert response.json()["code"] == "master-required"
    assert response.json()["category"] == "token"
