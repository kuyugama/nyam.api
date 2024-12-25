from src.util import utc_timestamp
from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, team):
    response = await requests.teams.get_team(client, team.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        id=team.id,
        name=team.name,
        description=team.description,
        created_at=int(utc_timestamp(team.created_at)),
        updated_at=team.updated_at,
    )


async def test_none(client):
    response = await requests.teams.get_team(client, 0)
    print(response.json())
    assert response.status_code == 404
    assert_contain(
        response.json(),
        category="teams",
        code="not-found",
    )
