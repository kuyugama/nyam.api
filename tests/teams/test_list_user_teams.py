from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, team, member_owner):
    response = await requests.teams.list_user_teams(client, member_owner.user.nickname)
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        pagination={
            "pages": 1,
            "page": 1,
            "total": 1,
        },
    )

    assert_contain(
        response.json()["items"][0],
        id=team.id,
        name=team.name,
        description=team.description,
    )
