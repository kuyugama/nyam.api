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
