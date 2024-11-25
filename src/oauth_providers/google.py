from typing import Any

from aiohttp import ClientSession
from starlette.datastructures import URL

from config import settings
from .base import BaseOAuthProvider, OAuthUser, OAuthToken, oauth_error
from ..util import slugify, email_to_nickname


class GoogleOAuthProvider(BaseOAuthProvider):
    requires_redirect_url = True

    def __init__(
        self,
        auth_url: str,
        token_url: str,
        user_url: str,
        scopes: list[str],
        redirect_url: str,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.redirect_url = redirect_url
        self.auth_url = auth_url
        self.token_url = token_url
        self.user_url = user_url
        self.scopes = scopes

    def get_url(self) -> str:
        return (
            URL(self.auth_url)
            .replace_query_params(
                scope=" ".join(self.scopes),
                response_type="code",
                access_type="offline",
                client_id=settings.auth_secrets.google.client.id,
                redirect_uri=self.redirect_url,
            )
            .components.geturl()
        )

    async def callback(self, query: dict[str, Any]) -> OAuthToken:
        if query.get("code"):
            client = ClientSession()
            async with client:
                resp = await client.post(
                    self.token_url,
                    data=dict(
                        grant_type="authorization_code",
                        client_id=settings.auth_secrets.google.client.id,
                        client_secret=settings.auth_secrets.google.client.secret,
                        code=query.get("code"),
                        redirect_uri=self.redirect_url,
                    ),
                )
                json = await resp.json()

            if "error" not in json:
                return OAuthToken(
                    access_token=json.get("access_token"),
                    token_type=json.get("token_type"),
                    refresh_token=None,
                    refresh_after=None,
                    refresh_before=None,
                )
            else:
                query["error"] = json["error"]

        match query.get("error"):
            case "access_denied":
                raise oauth_error(extra=dict(message="Access denied"))
            case "admin_policy_enforced":
                raise oauth_error(extra=dict(message="Access denied by workspace admin"))
            case "disallowed_useragent":
                raise oauth_error(extra=dict(message="Disallowed user agent"))
            case "org_internal":
                raise oauth_error(extra=dict(message="Access denied"))
            case "invalid_client":
                raise oauth_error(extra=dict(message="Invalid client secret provided"))
            case "redirect_uri_mismatch":
                raise oauth_error(extra=dict(message="Redirect uri mismatch"))
            case "invalid_request":
                raise oauth_error(extra=dict(message="Invalid request"))
            case "invalid_grant":
                raise oauth_error(extra=dict(message="Invalid authorization code"))
            case _:
                raise oauth_error(extra=dict(message=query.get("error")))

    async def get_user(self, token: OAuthToken) -> OAuthUser:
        client = ClientSession()
        async with client:
            resp = await client.get(
                self.user_url,
                headers={
                    "Authorization": f"{token.token_type} {token.access_token}",
                },
            )
            json = await resp.json()

        nickname = email_to_nickname(json["email"])

        return OAuthUser(
            id=json["id"],
            nickname=nickname,
            email=json["email"],
        )
