from pydantic import HttpUrl

from src.scheme import OAuthProvider


class FullOAuthProvider(OAuthProvider):
    url: HttpUrl
