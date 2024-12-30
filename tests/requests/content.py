from typing import BinaryIO

from async_asgi_testclient import TestClient
from async_asgi_testclient.response import Response


async def list_providers(client: TestClient) -> Response:
    return await client.get("/content/providers")


async def search_composition_in_provider(
    client: TestClient, provider_name: str, query: str, page: int = 1
) -> Response:
    return await client.get(
        f"/content/composition/{provider_name}/search", query_string={"query": query, "page": page}
    )


async def publish_composition_from_provider(
    client: TestClient, provider_name: str, provider_id: str
) -> Response:
    return await client.put(f"/content/composition/{provider_name}/{provider_id}")


async def composition_by_slug(client: TestClient, slug: str) -> Response:
    return await client.get(f"/content/composition/{slug}")


async def list_compositions(
    client: TestClient,
    tags: list[str] | None = None,
    genres: list[str] | None = None,
    styles: list[str] | None = None,
    years: tuple[int, int] | None = None,
    tags_exclude: list[str] | None = None,
    volumes: tuple[int, int] | None = None,
    chapters: tuple[int, int] | None = None,
    genres_exclude: list[str] | None = None,
) -> Response:
    return await client.post(
        "/content/composition/list",
        json={
            "tags": tags,
            "years": years,
            "styles": styles,
            "genres": genres,
            "volumes": volumes,
            "chapters": chapters,
            "tags_exclude": tags_exclude,
            "genres_exclude": genres_exclude,
        },
    )


async def publish_composition_variant(
    client: TestClient,
    token: str,
    team_id: int,
    slug: str,
    title: str,
    synopsis: str,
) -> Response:
    return await client.post(
        f"/content/composition/{slug}/variant",
        json={
            "title": title,
            "synopsis": synopsis,
            "team_id": team_id,
        },
        headers={"Token": token},
    )


async def list_composition_variants(client: TestClient, slug: str, page: int = 1) -> Response:
    return await client.get(
        f"/content/composition/variant/list/{slug}", query_string={"page": page}
    )


async def get_composition_variant(client: TestClient, variant_id: int) -> Response:
    return await client.get(f"/content/composition/variant/{variant_id}")


async def create_volume(
    client: TestClient,
    token: str,
    variant_id: int,
    index: int | None = None,
    title: str | None = None,
) -> Response:
    return await client.post(
        f"/content/composition/variant/{variant_id}/volume",
        json={"index": index, "title": title},
        headers={"Token": token},
    )


async def list_volumes(client: TestClient, variant_id: int, page: int = 1) -> Response:
    return await client.get(
        f"/content/volume/list/{variant_id}",
        query_string={"page": page},
    )


async def get_volume(client: TestClient, volume_id: int) -> Response:
    return await client.get(f"/content/volume/{volume_id}")


async def create_chapter(
    client: TestClient,
    token: str,
    volume_id: int,
    index: int | None = None,
    title: str | None = None,
):
    return await client.post(
        f"/content/volume/{volume_id}/chapter",
        json={"index": index, "title": title},
        headers={"Token": token},
    )


async def list_chapters(client: TestClient, volume_id: int, page: int = 1) -> Response:
    return await client.get(
        f"/content/chapter/list/{volume_id}",
        query_string={"page": page},
    )


async def get_chapter(client: TestClient, chapter_id: int) -> Response:
    return await client.get(f"/content/chapter/{chapter_id}")


async def create_text_page(
    client: TestClient, token: str, chapter_id: int, text: str, index: int | None = None
) -> Response:
    return await client.post(
        f"/content/chapter/{chapter_id}/page/text",
        json={"index": index, "text": text},
        headers={"Token": token},
    )


async def create_image_page(
    client: TestClient, token: str, chapter_id: int, file: BinaryIO, index: int | None = None
) -> Response:
    query = {"index": index}
    if index is None:
        query = None

    return await client.post(
        f"/content/chapter/{chapter_id}/page/image",
        query_string=query,
        files={"file": (file.name, file)},
        headers={"Token": token},
    )


async def list_pages(client: TestClient, chapter_id: int, page: int = 1) -> Response:
    return await client.get(
        f"/content/page/list/{chapter_id}",
        query_string={"page": page},
    )


async def get_page(client: TestClient, page_id: int) -> Response:
    return await client.get(f"/content/page/{page_id}")
