from src import constants
from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, team, token_regular, member_regular, member_owner, token_translator):
    response = await requests.teams.join_team(client, token_regular.body, team.id)
    print("join request:", response.json())
    assert response.status_code == 200

    assert response.json()["status"] == constants.STATUS_TEAM_JOIN_PENDING

    response = await requests.teams.list_joins(client, token_translator.body, team.id)
    print("list joins:", response.json())
    assert response.status_code == 200

    assert_contain(response.json()["pagination"], page=1, pages=1, total=1)

    assert_contain(
        response.json()["items"][0],
        recursive=True,
        user={
            "id": token_regular.owner_id,
        },
        status=constants.STATUS_TEAM_JOIN_PENDING,
    )
