from src import constants
from tests import requests
from tests.helpers import assert_contain


async def test_no_origin(client, token_translator, member_owner, team):
    response = await requests.content.publish_composition_variant(
        client, token_translator.body, team.id, "slug", "sometitle", "somesynospis"
    )
    print(response.json())
    assert response.status_code == 404
    assert_contain(response.json(), category="content/composition", code="not-found")


async def test_normal(client, token_translator, member_owner, team, composition):
    title = "sometitle"
    synopsis = "somesynopsis"

    response = await requests.content.publish_composition_variant(
        client, token_translator.body, team.id, composition.slug, title, synopsis
    )
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title=title,
        synopsis=synopsis,
        volumes=0,
        chapters=0,
        status=constants.STATUS_COMPOSITION_VARIANT_PENDING,
    )
