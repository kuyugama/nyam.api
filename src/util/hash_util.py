from hashlib import sha256
from typing import Any


def cache_key_hash(cache_key: tuple[Any, ...] | None) -> str:
    """Generate hash of cache key"""
    hash_ = sha256()

    if isinstance(cache_key, str):
        hash_.update(cache_key.encode("utf-8"))

    if isinstance(cache_key, int):
        # Range: -170141183460469231731687303715884105727, 170141183460469231731687303715884105727
        hash_.update(cache_key.to_bytes(16, signed=True))

    if isinstance(cache_key, tuple):
        hash_.update(len(cache_key).to_bytes())
        for i in cache_key:
            hash_.update(cache_key_hash(i).encode("utf-8"))

    return hash_.hexdigest()
