from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, token_translator, team, member_owner):

    name = "New name"
    description = "New description"
    response = await requests.teams.update_team(
        client, token_translator.body, team.id, name=name, description=description
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        name=name,
        description=description,
    )
