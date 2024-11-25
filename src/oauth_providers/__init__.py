import importlib
from typing import Any, TypedDict

from config import settings
from .base import BaseOAuthProvider, OAuthToken, OAuthUser


__all__ = [
    "OAuthUser",
    "OAuthToken",
    "get_provider",
    "provider_registry",
    "BaseOAuthProvider",
]


class _ProviderRegistryEntry(TypedDict):
    identifier: str
    name: str
    description: str
    class_: type[BaseOAuthProvider]
    args: dict[str, Any]


provider_registry: dict[str, _ProviderRegistryEntry] = {}


for provider_name in settings.oauth_providers:
    provider = settings.oauth_providers[provider_name]

    args: dict[str, Any] = dict(provider.args)

    module = importlib.import_module("src.oauth_providers." + provider_name)
    class_ = getattr(module, provider.classname)

    provider_registry[provider_name] = {
        "name": provider.name,
        "description": provider.description,
        "identifier": provider_name,
        "class_": class_,
        "args": args,
    }


def get_provider(name: str) -> _ProviderRegistryEntry | None:
    return provider_registry.get(name, None)
