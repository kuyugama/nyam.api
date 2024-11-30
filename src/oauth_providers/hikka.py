from dataclasses import replace
from datetime import timedelta
from typing import Any

from aiohttp import ClientSession
from starlette.datastructures import URL

from config import settings
from src.util import now, from_utc_timestamp
from .base import BaseOAuthProvider, oauth_error, OAuthUser, OAuthToken


class HikkaOAuthProvider(BaseOAuthProvider):
    def __init__(self, auth_url: str, api_url: str, scopes: list[str], **kwargs) -> None:
        super().__init__(**kwargs)

        self.auth_url = auth_url
        self.api_url = api_url
        self.scopes = scopes

    def get_url(self) -> str:
        return (
            URL(self.auth_url)
            .replace_query_params(
                reference=settings.oauth_secrets.hikka.client.id, scope=",".join(self.scopes)
            )
            .components.geturl()
        )

    async def callback(self, query: dict[str, Any]) -> OAuthToken:
        now_ = now()

        client = ClientSession(self.api_url)
        async with client:
            resp = await client.post(
                "/auth/token",
                json={
                    "request_reference": query["reference"],
                    "client_secret": settings.oauth_secrets.hikka.client.secret,
                },
            )

            json = await resp.json()

        if resp.status != 200:
            raise oauth_error(extra=dict(message=json["message"]))

        expire_at = from_utc_timestamp(json["expiration"])
        expires_in = expire_at - now_
        return OAuthToken(
            access_token=json["secret"],
            refresh_token=None,
            token_type=None,
            refresh_after=now_ + expires_in / 2,
            refresh_before=expire_at,
            save_token=True,
        )

    async def get_user(self, token: OAuthToken) -> OAuthUser:
        client = ClientSession(self.api_url)
        async with client:
            resp = await client.get(
                "/user/me",
                headers={"Auth": token.access_token},
            )
            json = await resp.json()

        if resp.status != 200:
            raise oauth_error(extra=dict(message=json["message"]))

        return OAuthUser(id=json["reference"], nickname=json["username"])

    async def refresh_token(self, token: OAuthToken) -> OAuthToken:
        now_ = now()

        client = ClientSession(self.api_url)
        async with client:
            resp = await client.get(
                "/user/me",
                headers={"Auth": token.access_token},
            )

            json = await resp.json()

        if resp.status != 200:
            raise oauth_error(extra=dict(message=json["message"]))

        valid_for = timedelta(days=7)

        return replace(
            token,
            refresh_after=now_ + valid_for / 2,
            refresh_before=now_ + valid_for,
        )
