from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response


async def signup(client: TestClient, email: str, nickname: str, password: str) -> Response:
    return await client.post(
        "/auth/signup",
        json={
            "email": email,
            "nickname": nickname,
            "password": password,
        },
    )


async def signin(
    client: TestClient, email: str | None, nickname: str | None, password: str
) -> Response:
    return await client.post(
        "/auth/signin",
        json={
            "email": email,
            "nickname": nickname,
            "password": password,
        },
    )


async def token_info(
    client: TestClient,
    token: str,
) -> Response:
    return await client.get(
        "/auth/token/info",
        headers={"Token": token},
    )


async def list_oauth_providers(client: TestClient) -> Response:
    return await client.get(
        "/auth/oauth/providers",
    )


async def oauth_authorize(client: TestClient, provider: str, query: dict[str, str]) -> Response:
    return await client.post(
        f"/auth/oauth/{provider}",
        query_string=query,
    )


async def oauth_get_provider(client: TestClient, provider: str) -> Response:
    return await client.get(
        f"/auth/oauth/{provider}",
    )
