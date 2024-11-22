from hashlib import sha256
from typing import Any


def cache_key_hash(cache_key: tuple[Any, ...] | None) -> str:
    """Generate hash of cache key"""
    hash_ = sha256()

    if isinstance(cache_key, str):
        hash_.update(cache_key.encode("utf-8"))

    if isinstance(cache_key, int):
        hash_.update(cache_key.to_bytes())

    if isinstance(cache_key, tuple):
        hash_.update(len(cache_key).to_bytes())
        for i in cache_key:
            hash_.update(cache_key_hash(i).encode("utf-8"))

    return hash_.hexdigest()
