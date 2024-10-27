from tests import requests


async def test_normal(client, user_regular):
    response = await requests.users.user(client, user_regular.nickname)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["id"] == user_regular.id
    assert response.json()["nickname"] == user_regular.nickname


async def test_non_existent(client, user_regular):
    response = await requests.users.user(client, user_regular.nickname + "-invalid")
    print(response.json())
    assert response.status_code == 404

    assert response.json()["category"] == "users"
    assert response.json()["code"] == "not-found"
