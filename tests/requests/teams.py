from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response


async def list_teams(client: TestClient, page: int = 1) -> Response:
    return await client.get("/teams/", query_string={"page": page})


async def get_team(client: TestClient, team_id: int) -> Response:
    return await client.get(f"/teams/{team_id}")


async def list_team_members(client: TestClient, team_id: int) -> Response:
    return await client.get(f"/teams/{team_id}/members/")


async def list_user_teams(client: TestClient, nickname: str, page: int = 1) -> Response:
    return await client.get(f"/teams/user/{nickname}", query_string={"page": page})


async def list_my_teams(client: TestClient, token: str, page: int = 1) -> Response:
    return await client.get(
        f"/teams/my",
        query_string={"page": page},
        headers={"Token": token},
    )


async def create_team(client: TestClient, token: str, name: str, description: str) -> Response:
    return await client.post(
        "/teams/",
        json={
            "name": name,
            "description": description,
        },
        headers={"Token": token},
    )


async def update_team(
    client: TestClient,
    token: str,
    team_id: int,
    name: str | None = None,
    description: str | None = None,
) -> Response:
    return await client.patch(
        f"/teams/{team_id}",
        json={
            "name": name,
            "description": description,
        },
        headers={"Token": token},
    )


async def join_team(client: TestClient, token: str, team_id: int) -> Response:
    return await client.post(
        f"/teams/{team_id}/joins",
        headers={"Token": token},
    )


async def list_joins(client: TestClient, token: str, team_id: int, page: int = 1) -> Response:
    return await client.get(
        f"/teams/{team_id}/joins",
        query_string={"page": page},
        headers={"Token": token},
    )


async def accept_join(client: TestClient, token: str, team_id: int, join_id: int) -> Response:
    return await client.post(
        f"/teams/{team_id}/joins/{join_id}/accept",
        headers={"Token": token},
    )


async def reject_join(client: TestClient, token: str, team_id: int, join_id: int) -> Response:
    return await client.post(
        f"/teams/{team_id}/joins/{join_id}/reject",
        headers={"Token": token},
    )


async def kick_member(client: TestClient, token: str, team_id: int, nickname: str):
    return await client.delete(
        f"/teams/{team_id}/members/{nickname}",
        headers={"Token": token},
    )


async def update_member(
    client: TestClient,
    token: str,
    team_id: int,
    nickname: str,
    pseudonym: str | None = None,
    permissions: str | None = None,
    permissions_merge: str | None = None,
    role: str | None = None,
):
    return await client.patch(
        f"/teams/{team_id}/members/{nickname}",
        headers={"Token": token},
        json={
            "permissions": permissions,
            "permissions_merge": permissions_merge,
            "role": role,
            "pseudonym": pseudonym,
        },
    )


async def leave_team(client: TestClient, token: str, team_id: int):
    return await client.post(
        f"/teams/{team_id}/leave",
        headers={"Token": token},
    )


async def verify_team(client: TestClient, token: str, team_id: int):
    return await client.post(
        f"/teams/{team_id}/verify",
        headers={"Token": token},
    )


async def unverify_team(client: TestClient, token: str, team_id: int):
    return await client.delete(
        f"/teams/{team_id}/verify",
        headers={"Token": token},
    )
