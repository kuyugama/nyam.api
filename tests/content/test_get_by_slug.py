from tests import requests
from tests.helpers import assert_contain


async def test_normal_composition(client, composition):
    response = await requests.content.composition_by_slug(client, composition.slug)
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        title_uk=composition.title_uk,
        title_en=composition.title_en,
        title_original=composition.title_original,
        title=composition.title,
        synopsis_uk=composition.synopsis_uk,
        synopsis_en=composition.synopsis_en,
        synopsis=composition.synopsis,
        genres=composition.genres,
        tags=composition.tags,
        nsfw=composition.nsfw,
        mal_id=composition.mal_id,
        provider=composition.provider,
        provider_id=composition.provider_id,
        style=composition.style,
        score=composition.score,
        scored_by=composition.scored_by,
        chapters=composition.chapters,
        volumes=composition.volumes,
        variants=composition.variants,
        id=composition.id,
    )
