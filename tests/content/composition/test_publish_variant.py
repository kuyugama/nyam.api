from src import constants
from tests import requests
from tests.helpers import assert_contain


async def test_no_origin(client, token_admin):
    response = await requests.content.publish_composition_variant(
        client, token_admin.body, "slug", "sometitle", "somesynospis"
    )
    print(response.json())
    assert response.status_code == 404

    assert response.json()["category"] == "content/composition"
    assert response.json()["code"] == "composition-not-found"


async def test_normal(client, token_admin, composition):
    title = "sometitle"
    synopsis = "somesynopsis"

    response = await requests.content.publish_composition_variant(
        client, token_admin.body, composition.slug, title, synopsis
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
