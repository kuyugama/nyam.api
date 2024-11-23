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
    slug: str,
    title: str,
    synopsis: str,
) -> Response:
    return await client.post(
        f"/content/composition/{slug}/variant",
        json={
            "title": title,
            "synopsis": synopsis,
        },
        headers={"Token": token},
    )


async def list_composition_variants(client: TestClient, slug: str, page: int = 1) -> Response:
    return await client.get(
        f"/content/composition/variant/list/{slug}", query_string={"page": page}
    )


async def get_composition_variant(client: TestClient, variant_id: int) -> Response:
    return await client.get(f"/content/composition/variant/{variant_id}")
