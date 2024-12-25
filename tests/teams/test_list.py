from tests import requests
from src.util import utc_timestamp
from tests.helpers import assert_contain


async def test_normal(client, team):
    response = await requests.teams.list_teams(
        client,
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        pagination={
            "page": 1,
            "pages": 1,
            "total": 1,
        },
    )

    assert_contain(
        response.json()["items"][0],
        name=team.name,
        description=team.description,
        verified=team.verified,
        id=team.id,
        created_at=int(utc_timestamp(team.created_at)),
        updated_at=team.updated_at,
    )


async def test_none(client):
    response = await requests.teams.list_teams(client)
    print(response.json())
    assert response.status_code == 200
    assert_contain(
        response.json(),
        pagination={
            "page": 1,
            "pages": 0,
            "total": 0,
        },
        items=[],
    )
