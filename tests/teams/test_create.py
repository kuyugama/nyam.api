from tests import requests
from tests.helpers import assert_contain


async def test_normal(client, token_translator):
    name = "Test Team"
    description = "Test description"
    response = await requests.teams.create_team(
        client, token_translator.body, name=name, description=description
    )
    print(response.json())

    assert response.status_code == 200

    assert_contain(
        response.json(),
        name=name,
        description=description,
    )
