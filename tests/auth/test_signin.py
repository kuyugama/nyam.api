from async_asgi_testclient import TestClient

from src.ratelimit import memory_store
from tests import requests


async def test_normal_email(client: TestClient, user_regular, password_user):
    response = await requests.auth.signin(client, user_regular.email, None, password_user)
    print(response.json())
    assert response.status_code == 200

    assert response.json().get("token")
    assert response.json().get("expire_at")
    assert response.json().get("used_at") is None


async def test_normal_nickname(client: TestClient, user_regular, password_user):
    response = await requests.auth.signin(client, None, user_regular.nickname, password_user)
    print(response.json())
    assert response.status_code == 200

    assert response.json().get("token")
    assert response.json().get("expire_at")
    assert response.json().get("used_at") is None


async def test_incorrect_password(client: TestClient, user_regular, password_user, x_real_ip):
    response = await requests.auth.signin(
        client, user_regular.email, None, "incorrect_" + password_user
    )
    print(response.json())
    assert response.status_code == 400

    assert response.json().get("code") == "password-incorrect"
    assert response.json().get("category") == "auth"

    endpoint = await memory_store().get_user_endpoint("/auth/signin", "POST", x_real_ip)
    assert endpoint is not None
    assert len(endpoint.hits) == 1
    assert not endpoint.blocked


async def test_nonexistent(client: TestClient, user_regular, password_user):
    response = await requests.auth.signin(
        client, "non_existent_" + user_regular.email, None, password_user
    )
    print(response.json())
    assert response.status_code == 404

    assert response.json().get("code") == "user-not-found"
    assert response.json().get("category") == "auth"
