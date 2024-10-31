from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response


async def create_role(
    client: TestClient,
    master_key: str,
    name: str,
    title: str,
    default: bool = False,
    permissions: dict[str, bool] = None,
    base_role: str = None,
) -> Response:
    if permissions is None:
        permissions = {}

    return await client.post(
        "/roles/",
        headers={"Master-Key": master_key},
        json={
            "name": name,
            "title": title,
            "default": default,
            "permissions": permissions,
            "base_role": base_role,
        },
    )


async def list_roles(client: TestClient) -> Response:
    return await client.get("/roles")


async def update_role(
    client: TestClient,
    master_key: str,
    name: str,
    title: str | None = None,
    default: bool = False,
    permissions: dict[str, bool] = None,
    merge_permissions: bool = False,
):
    return await client.patch(
        f"/roles/{name}",
        headers={"Master-Key": master_key},
        json={
            "default": default,
            "title": title,
            "permissions": permissions,
            "merge_permissions": merge_permissions,
        },
    )


async def delete_role(
    client: TestClient,
    master_key: str,
    name: str,
    replacement: str | None = None,
):
    return await client.delete(
        f"/roles/{name}",
        query_string={"replacement": replacement} if replacement else None,
        headers={"Master-Key": master_key},
    )
