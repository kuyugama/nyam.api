import operator
from functools import partial

import bcrypt


def camel_to_snake(name):
    return "".join(
        "_" + char.lower() if char.isupper() and i != 0 else char.lower()
        for i, char in enumerate(name)
    )


def consists_of(source: str, characters: str) -> bool:
    return all(
        map(
            partial(
                operator.contains,
                characters,
            ),
            source,
        )
    )


def secure_hash(payload: str) -> str:
    return bcrypt.hashpw(payload.encode(), bcrypt.gensalt()).decode()


def verify_payload(payload: str, payload_hash: str) -> bool:
    return bcrypt.checkpw(payload.encode(), payload_hash.encode())
