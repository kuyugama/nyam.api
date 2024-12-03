import secrets
import uuid

import pytest

from tests import requests, helpers
from src.oauth_providers import OAuthToken, OAuthUser

from config import settings
from unittest.mock import patch, AsyncMock

from tests.helpers import assert_contain


@pytest.fixture(scope="module")
def oauth_user(email_user_unverified) -> OAuthUser:
    return OAuthUser(
        secrets.token_hex(32),
        nickname=helpers.email_to_nickname(email_user_unverified),
        email=email_user_unverified,
    )


@pytest.fixture(scope="module", autouse=True)
def mock_provider(oauth_user):
    patcher = patch("src.oauth_providers.get_provider_instance")

    get_provider_instance = patcher.start()

    instance = get_provider_instance.return_value

    instance.callback = AsyncMock(
        return_value=OAuthToken(
            access_token="token",
            token_type="Bearer",
            refresh_token=None,
            refresh_after=None,
            refresh_before=None,
        )
    )

    instance.get_user = AsyncMock(return_value=oauth_user)

    yield

    patcher.stop()


@pytest.mark.parametrize("provider", settings.oauth_providers.keys())
async def test_normal(client, role_unverified, provider, oauth_user):
    match provider:
        case "hikka":
            query = {"reference": uuid.uuid4()}
        case "google":
            query = {"code": secrets.token_hex(16)}
        case _:
            query = {}

    response = await requests.auth.oauth_authorize(client, provider, query)
    print("OAuth signin response", response.json())
    assert response.status_code == 200

    token = response.json()["token"]

    response = await requests.users.me(client, token)
    print("User me response", response.json())
    assert response.status_code == 200

    assert_contain(
        response.json(),
        nickname=oauth_user.nickname,
        email=oauth_user.email,
    )


@pytest.mark.parametrize("provider", settings.oauth_providers.keys())
async def test_nickname_occupied(
    client, role_unverified, user_regular, provider, oauth_user, session
):
    user_regular.nickname = oauth_user.nickname
    await session.commit()

    match provider:
        case "hikka":
            query = {"reference": uuid.uuid4()}
        case "google":
            query = {"code": secrets.token_hex(16)}
        case _:
            query = {}

    response = await requests.auth.oauth_authorize(client, provider, query)
    print("OAuth signin response", response.json())
    assert response.status_code == 200

    token = response.json()["token"]

    response = await requests.users.me(client, token)
    print("User me response", response.json())
    assert response.status_code == 200

    # Must be DIFFERENT user
    assert response.json()["email"] == oauth_user.email
    assert response.json()["nickname"] != oauth_user.nickname
    assert response.json()["id"] != user_regular.id


@pytest.mark.parametrize("provider", settings.oauth_providers.keys())
async def test_same_email(client, role_unverified, user_regular, provider, oauth_user, session):
    user_regular.email = oauth_user.email
    await session.commit()

    match provider:
        case "hikka":
            query = {"reference": uuid.uuid4()}
        case "google":
            query = {"code": secrets.token_hex(16)}
        case _:
            query = {}

    response = await requests.auth.oauth_authorize(client, provider, query)
    print("OAuth signin response", response.json())
    assert response.status_code == 200

    token = response.json()["token"]

    response = await requests.users.me(client, token)
    print("User me response", response.json())
    assert response.status_code == 200

    # Must be the SAME user
    assert_contain(
        response.json(),
        id=user_regular.id,
        email=user_regular.email,
        nickname=user_regular.nickname,
    )
