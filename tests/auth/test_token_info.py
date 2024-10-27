from async_asgi_testclient import TestClient

from src.util import utc_timestamp
from tests import requests


async def test_normal(client: TestClient, token_regular):
    response = await requests.auth.token_info(client, token_regular.body)
    print(response.json())
    assert response.status_code == 200

    assert response.json().get("token") == token_regular.body
    assert response.json().get("expire_at") == int(utc_timestamp(token_regular.expire_at))
    assert response.json().get("used_at") == token_regular.used_at
    assert response.json().get("owner", {}).get("id") == token_regular.owner.id


async def test_nonexistent(client: TestClient):
    response = await requests.auth.token_info(client, "non-existent")
    print(response.json())
    assert response.status_code == 401

    assert response.json().get("code") == "required"
    assert response.json().get("category") == "token"


async def test_expired(client: TestClient, expired_token):
    response = await requests.auth.token_info(client, expired_token.body)
    print(response.json())
    assert response.status_code == 401

    assert response.json().get("code") == "expired"
    assert response.json().get("category") == "token"
