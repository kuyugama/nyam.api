from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response


__all__ = [
    "me",
    "user",
    "update_own_info",
]


async def me(client: TestClient, token: str) -> Response:
    return await client.get(
        "/users/me",
        headers={"Token": token},
    )


async def update_own_info(
    client: TestClient,
    token: str,
    nickname: str | None = None,
    pseudonym: str | None = None,
    description: str | None = None,
    remove_pseudonym: bool = False,
    remove_description: bool = False,
    remove_avatar: bool = False,
) -> Response:
    return await client.patch(
        "/users/me",
        headers={"Token": token},
        json={
            "nickname": nickname,
            "pseudonym": pseudonym,
            "description": description,
            "remove_avatar": remove_avatar,
            "remove_pseudonym": remove_pseudonym,
            "remove_description": remove_description,
        },
    )


async def user(client: TestClient, nickname: str) -> Response:
    return await client.get(f"/users/{nickname}")


async def update_others_info(
    client: TestClient,
    token: str,
    nickname: str,
    new_nickname: str | None = None,
    new_description: str | None = None,
    new_pseudonym: str | None = None,
    remove_pseudonym: bool = False,
    remove_description: bool = False,
    remove_avatar: bool = False,
    permissions: dict[str, bool] = None,
    merge_permissions: bool = False,
) -> Response:
    return await client.patch(
        f"/users/{nickname}",
        headers={"Token": token},
        json={
            "nickname": new_nickname,
            "pseudonym": new_pseudonym,
            "permissions": permissions,
            "description": new_description,
            "remove_avatar": remove_avatar,
            "remove_pseudonym": remove_pseudonym,
            "merge_permissions": merge_permissions,
            "remove_description": remove_description,
        },
    )
