from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, member_owner, member_regular, token_translator):
    response = await requests.teams.kick_member(
        client, token_translator.body, member_regular.team_id, member_regular.user.nickname
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        id=member_regular.user.id,
    )
