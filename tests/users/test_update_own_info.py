import secrets

from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, token_regular, user_regular):
    new_nickname = secrets.token_hex(5)
    new_pseudonym = secrets.token_hex(5)
    new_description = secrets.token_hex(10)

    response = await requests.users.update_own_info(
        client, token_regular.body, new_nickname, new_pseudonym, new_description
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["nickname"] == new_nickname
    assert response.json()["pseudonym"] == new_pseudonym
    assert response.json()["description"] == new_description


async def test_remove_info(client, token_regular, user_regular):
    # Ensure user has the pseudonym and description:
    response = await requests.users.update_own_info(
        client, token_regular.body, None, "pseudonym", "description"
    )
    print(response.json())

    # Remove pseudonym and description here:
    response = await requests.users.update_own_info(
        client, token_regular.body, remove_pseudonym=True, remove_description=True
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pseudonym"] is None
    assert response.json()["description"] is None


async def test_empty(client, token_regular):
    response = await requests.users.update_own_info(client, token_regular.body)
    print(response.json())
    assert response.status_code == 400

    assert_contain(
        response.json(),
        category="users",
        code="empty-update"
    )


async def test_nothing_to_update(client, token_regular, user_regular):
    response = await requests.users.update_own_info(
        client,
        token_regular.body,
        user_regular.nickname,
        user_regular.pseudonym,
        user_regular.description,
    )
    print(response.json())
    assert response.status_code == 400

    assert_contain(
        response.json(),
        category="users",
        code="nothing-to-update"
    )
