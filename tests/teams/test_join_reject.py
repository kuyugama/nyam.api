from src import constants
from tests import requests


async def test_normal(client, team, token_regular, member_regular, member_owner, token_translator):
    response = await requests.teams.join_team(client, token_regular.body, team.id)
    print("join request:", response.json())
    assert response.status_code == 200

    assert response.json()["status"] == constants.STATUS_TEAM_JOIN_PENDING

    response = await requests.teams.reject_join(
        client, token_translator.body, team.id, response.json()["id"]
    )
    print("accept request:", response.json())
    assert response.status_code == 200

    assert response.json()["status"] == constants.STATUS_TEAM_JOIN_REJECTED
