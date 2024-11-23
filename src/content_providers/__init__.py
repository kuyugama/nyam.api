import importlib
from typing import Any, TypedDict

from config import settings
from .base import BaseContentProvider, ContentProviderComposition, SearchEntry


__all__ = [
    "SearchEntry",
    "get_provider",
    "provider_registry",
    "BaseContentProvider",
    "ContentProviderComposition",
]


class _ProviderRegistryEntry(TypedDict):
    identifier: str
    name: str
    description: str
    class_: type[BaseContentProvider]
    args: dict[str, Any]


provider_registry: dict[str, _ProviderRegistryEntry] = {}


for provider_name in settings.content_providers:
    provider = settings.content_providers[provider_name]

    args: dict[str, Any] = dict(provider.args)

    module = importlib.import_module("src.content_providers." + provider_name)
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
