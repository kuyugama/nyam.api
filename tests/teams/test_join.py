from src import constants
from tests import requests


async def test_normal(client, team, token_regular):
    response = await requests.teams.join_team(client, token_regular.body, team.id)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["status"] == constants.STATUS_TEAM_JOIN_PENDING
