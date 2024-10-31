import secrets

from tests import requests

from async_asgi_testclient import TestClient


async def test_normal(client: TestClient, role_unverified, password_user):
    response = await requests.auth.signup(client, "pec@mail.com", "pecpec", password_user)
    print(response.json())
    assert response.status_code == 200

    assert response.json().get("token")
    assert response.json().get("expire_at")
    assert response.json().get("used_at") is None


async def test_existing_user_email(
    client: TestClient, user_regular, role_unverified, password_user
):
    response = await requests.auth.signup(
        client, user_regular.email, secrets.token_hex(16), password_user
    )
    print(response.json())
    assert response.status_code == 400

    error = response.json()

    assert error.get("code") == "email-occupied"
    assert error.get("category") == "auth"


async def test_existing_user_nickname(
    client: TestClient, user_regular, role_unverified, password_user
):
    response = await requests.auth.signup(
        client,
        secrets.token_hex(16) + "@mail.com",
        user_regular.nickname,
        password_user,
    )
    print(response.json())
    assert response.status_code == 400

    error = response.json()

    assert error.get("code") == "nickname-occupied"
    assert error.get("category") == "auth"
