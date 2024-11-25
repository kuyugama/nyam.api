from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.scheme import define_error

oauth_error = define_error("oauth", "provider-error", "OAuth provider error: {message}", 401)


@dataclass(frozen=True)
class OAuthToken:
    access_token: str

    token_type: str | None
    refresh_token: str | None
    refresh_after: datetime | None
    refresh_before: datetime | None

    extra: dict[str, Any] = field(default_factory=dict)

    save_token: bool = False


@dataclass(frozen=True)
class OAuthUser:
    id: str

    nickname: str
    email: str | None = None


class BaseOAuthProvider(ABC):
    requires_redirect_url: bool = False

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def get_url(self) -> str:
        """
        Generate sing-in url for this provider
        """
        raise NotImplementedError

    @abstractmethod
    async def callback(self, query: dict[str, Any]) -> OAuthToken:
        """
        Handle oauth callback

        :param query: query params (e.g. {"code": "aabbcc11223344"} )
        :return: oauth token or raise an APIError exception
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, token: OAuthToken) -> OAuthUser:
        """
        Get user by token

        :return: user object
        """
        raise NotImplementedError

    async def refresh_token(self, token: OAuthToken) -> OAuthToken:
        """
        Refresh token. This is called only for tokens that set "save_token=True"

        :return: new or refreshed token
        """
        raise NotImplementedError
