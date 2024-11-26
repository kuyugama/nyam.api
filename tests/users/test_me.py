from async_asgi_testclient import TestClient

from src.util import utc_timestamp
from src import permissions
from tests import requests


async def test_normal(client: TestClient, user_regular, token_regular):
    response = await requests.users.me(client, token_regular.body)
    print(response.json())
    assert response.status_code == 200

    assert response.json() == {
        "email": user_regular.email,
        "nickname": user_regular.nickname,
        "pseudonym": user_regular.pseudonym,
        "description": user_regular.description,
        "avatar": user_regular.avatar,
        "online": user_regular.online,
        "role": {
            "name": user_regular.role.name,
            "title": user_regular.role.title,
            "weight": user_regular.role.weight,
        },
        "created_at": int(utc_timestamp(user_regular.created_at)),
        "permissions": {permissions.user.own.update_info: True},
        "updated_at": user_regular.updated_at,
        "id": user_regular.id,
    }


async def test_invalid_token(client: TestClient):
    response = await requests.users.me(client, "invalid token")
    print(response.json())
    assert response.status_code == 401

    assert response.json().get("code") == "required"
    assert response.json().get("category") == "token"
