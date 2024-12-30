from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, member_owner, token_translator):
    response = await requests.teams.list_my_teams(client, token_translator.body)
    print(response.json())
    assert response.status_code == 200

    assert_contain(response.json(), pagination={"page": 1, "pages": 1, "total": 1})

    assert_contain(
        response.json()["items"][0],
        id=member_owner.team.id,
        name=member_owner.team.name,
        description=member_owner.team.description,
    )
