import secrets

from tests import requests, helpers


async def test_normal(client, user_regular, token_moderator):
    new_nickname = secrets.token_hex(5)
    new_description = secrets.token_hex(15)
    new_pseudonym = secrets.token_hex(10)
    response = await requests.users.update_others_info(
        client,
        token_moderator.body,
        user_regular.nickname,
        new_nickname,
        new_description,
        new_pseudonym,
    )
    print(response.json())
    assert response.status_code == 200

    helpers.assert_contain(
        response.json(), nickname=new_nickname, description=new_description, pseudonym=new_pseudonym
    )


async def test_no_rights(client, user_regular, token_regular):
    response = await requests.users.update_others_info(
        client, token_regular.body, user_regular.nickname, secrets.token_hex(10)
    )
    print(response.json())
    assert response.status_code == 403

    helpers.assert_contain(response.json(), category="permissions", code="denied")


async def test_update_permissions(client, user_regular, token_admin):
    new_permissions = {name: not allowed for name, allowed in user_regular.permissions.items()}
    response = await requests.users.update_others_info(
        client, token_admin.body, nickname=user_regular.nickname, permissions=new_permissions
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["permissions"] == new_permissions


async def test_update_permissions_no_rights(client, user_regular, token_moderator):
    new_permissions = {}
    response = await requests.users.update_others_info(
        client, token_moderator.body, user_regular.nickname, permissions=new_permissions
    )
    print(response.json())
    assert response.status_code == 403

    helpers.assert_contain(response.json(), category="permissions", code="denied")
