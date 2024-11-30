import pytest
from starlette.datastructures import URL

from tests import requests
from tests.helpers import assert_contain

from config import settings


@pytest.mark.parametrize("provider", settings.oauth_providers.keys())
async def test_normal(client, provider):
    response = await requests.auth.oauth_get_provider(client, provider)
    print(response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        name=settings.oauth_providers[provider].name,
        description=settings.oauth_providers[provider].description,
        identifier=provider,
    )

    url = URL(response.json()["url"])

    match provider:
        case "hikka":
            base_url = settings.oauth_providers.hikka.args.auth_url
            reference = settings.auth_secrets.hikka.client.id
            scope = settings.oauth_providers.hikka.args.scopes

            expected_url = URL(base_url).replace_query_params(
                reference=reference,
                scope=",".join(scope),
            )
            assert url == expected_url

        case "google":
            base_url = settings.oauth_providers.google.args.auth_url
            reference = settings.auth_secrets.google.client.id
            scope = settings.oauth_providers.google.args.scopes
            redirect_url = settings.oauth_providers.google.args.redirect_url

            expected_url = URL(base_url).replace_query_params(
                scope=" ".join(scope),
                response_type="code",
                access_type="offline",
                client_id=reference,
                redirect_uri=redirect_url,
            )

            assert url == expected_url
