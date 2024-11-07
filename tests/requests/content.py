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
):
    return await client.put(f"/content/composition/{provider_name}/{provider_id}")


async def composition_by_slug(client: TestClient, slug: str):
    return await client.get(f"/content/composition/{slug}")
