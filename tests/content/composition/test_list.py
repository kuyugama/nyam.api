from tests import requests
from tests.helpers import assert_composition


async def test_none(client):
    response = await requests.content.list_compositions(client)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 0,
        "pages": 0,
        "page": 1,
    }

    assert response.json()["items"] == []


async def test_empty_filters(client, composition):
    response = await requests.content.list_compositions(client)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 1,
        "pages": 1,
        "page": 1,
    }

    assert_composition(response.json()["items"][0], composition)


async def test_genres(client, composition, genre, session):
    composition.genres.append(genre)
    await session.commit()

    genres = [genre.slug for genre in composition.genres]

    response = await requests.content.list_compositions(client, genres=genres)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 1,
        "pages": 1,
        "page": 1,
    }

    assert_composition(response.json()["items"][0], composition)


async def test_genres_none(client, composition):
    genres = ["non-existent"]
    response = await requests.content.list_compositions(client, genres=genres)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 0,
        "pages": 0,
        "page": 1,
    }

    assert response.json()["items"] == []


async def test_tags(client, composition, session):
    composition.tags.append("tag")
    await session.commit()

    response = await requests.content.list_compositions(client, tags=composition.tags)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 1,
        "pages": 1,
        "page": 1,
    }

    assert_composition(response.json()["items"][0], composition)


async def test_tags_none(client, composition):
    tags = ["non-existent"]
    response = await requests.content.list_compositions(client, tags=tags)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 0,
        "pages": 0,
        "page": 1,
    }

    assert response.json()["items"] == []


async def test_years(client, composition):
    years = (composition.year - 1, composition.year + 1)

    response = await requests.content.list_compositions(client, years=years)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 1,
        "pages": 1,
        "page": 1,
    }

    assert_composition(response.json()["items"][0], composition)


async def test_years_none(client, composition):
    years = (composition.year - 2, composition.year - 1)

    response = await requests.content.list_compositions(client, years=years)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 0,
        "pages": 0,
        "page": 1,
    }

    assert response.json()["items"] == []


async def test_styles(client, composition):
    styles = [composition.style]

    response = await requests.content.list_compositions(client, styles=styles)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 1,
        "pages": 1,
        "page": 1,
    }

    assert_composition(response.json()["items"][0], composition)


async def test_styles_none(client, composition):
    styles = ["none"]

    response = await requests.content.list_compositions(client, styles=styles)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 0,
        "pages": 0,
        "page": 1,
    }
    assert response.json()["items"] == []


async def test_volumes(client, composition, session):
    composition.volumes = 10
    await session.commit()

    volumes = (composition.volumes - 1, composition.volumes + 1)

    response = await requests.content.list_compositions(client, volumes=volumes)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 1,
        "pages": 1,
        "page": 1,
    }

    assert_composition(response.json()["items"][0], composition)


async def test_volumes_none(client, composition):
    volumes = (11, 12)

    response = await requests.content.list_compositions(client, volumes=volumes)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 0,
        "pages": 0,
        "page": 1,
    }

    assert response.json()["items"] == []


async def test_chapters(client, composition, session):
    composition.chapters = 10
    await session.commit()

    chapters = (composition.chapters - 1, composition.chapters + 1)

    response = await requests.content.list_compositions(client, chapters=chapters)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 1,
        "pages": 1,
        "page": 1,
    }

    assert_composition(response.json()["items"][0], composition)


async def test_chapters_none(client, composition):
    chapters = (11, 12)

    response = await requests.content.list_compositions(client, chapters=chapters)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {
        "total": 0,
        "pages": 0,
        "page": 1,
    }

    assert response.json()["items"] == []
