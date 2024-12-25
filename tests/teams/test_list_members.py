from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, team, member_owner):
    response = await requests.teams.list_team_members(client, team.id)
    print(response.json())
    assert response.status_code == 200

    assert_contain(response.json(), pagination={"page": 1, "pages": 1, "total": 1})

    assert_contain(
        response.json()["items"][0],
        id=member_owner.id,
        pseudonym=member_owner.pseudonym,
    )

    assert response.json()["items"][0]["user"]["id"] == member_owner.user.id


async def test_no_team(client):
    response = await requests.teams.list_team_members(client, 0)
    print(response.json())
    assert response.status_code == 404

    assert_contain(response.json(), category="teams", code="not-found")
