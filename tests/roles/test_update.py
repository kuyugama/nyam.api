from src import permissions

from tests import requests


async def test_title(client, role_unverified, master_key):
    new_title = role_unverified.title + "-new"
    response = await requests.roles.update_role(
        client,
        master_key,
        role_unverified.name,
        new_title,
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["title"] == new_title


async def test_permissions(client, role_unverified, master_key):
    new_permissions = {permissions.user.own.update_info: True}
    response = await requests.roles.update_role(
        client,
        master_key,
        role_unverified.name,
        permissions=new_permissions,
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json()["permissions"] == new_permissions


async def test_permissions_merge(client, role_user, master_key):
    new_permissions = {permissions.user.update_info: True}
    response = await requests.roles.update_role(
        client,
        master_key,
        role_user.name,
        permissions=new_permissions,
        merge_permissions=True,
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json()["permissions"] == role_user.permissions | new_permissions
