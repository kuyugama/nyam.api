from src.permissions import permissions
from src.util import merge_permissions

from tests import requests
from tests.helpers import permissions_to_json


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
    assert response.json()["permissions"] == permissions_to_json(new_permissions)


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
    assert response.json()["permissions"] == permissions_to_json(
        merge_permissions(role_user.permissions, new_permissions)
    )
