from async_asgi_testclient import TestClient

from tests import requests


async def test_normal_email(client: TestClient, user_regular, user_password):
    response = await requests.auth.signin(client, user_regular.email, None, user_password)
    print(response.json())
    assert response.status_code == 200

    assert response.json().get("token")
    assert response.json().get("expire_at")
    assert response.json().get("used_at") is None


async def test_normal_nickname(client: TestClient, user_regular, user_password):
    response = await requests.auth.signin(client, None, user_regular.nickname, user_password)
    print(response.json())
    assert response.status_code == 200

    assert response.json().get("token")
    assert response.json().get("expire_at")
    assert response.json().get("used_at") is None


async def test_incorrect_password(client: TestClient, user_regular, user_password):
    response = await requests.auth.signin(
        client, user_regular.email, None, "incorrect_" + user_password
    )
    print(response.json())
    assert response.status_code == 400

    assert response.json().get("code") == "password-incorrect"
    assert response.json().get("category") == "auth"


async def test_nonexistent(client: TestClient, user_regular, user_password):
    response = await requests.auth.signin(
        client, "non_existent_" + user_regular.email, None, user_password
    )
    print(response.json())
    assert response.status_code == 404

    assert response.json().get("code") == "user-not-found"
    assert response.json().get("category") == "auth"
