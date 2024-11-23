from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, user_regular):
    response = await requests.users.user(client, user_regular.nickname)
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        id=user_regular.id,
        nickname=user_regular.nickname,
    )


async def test_non_existent(client, user_regular):
    response = await requests.users.user(client, user_regular.nickname + "-invalid")
    print(response.json())
    assert response.status_code == 404

    assert_contain(
        response.json(),
        category="users",
        code="not-found",
    )

