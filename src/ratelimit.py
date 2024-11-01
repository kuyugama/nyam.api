from functools import lru_cache

from fastapi import Depends
from ratelimit.user import UserID
from ratelimit.ranking.base import T
from ratelimit.endpoint import Endpoint
from ratelimit import BaseUser, BaseRanking, BaseStore

from src.models import Token
from src.scheme import ClientInfo
from src.dependencies import optional_token, client_details


class RatelimitUser(BaseUser):
    address: str
    user_id: int | None = None

    @property
    def unique_id(self):
        if self.user_id is None:
            return self.address

        return "{address}:{user_id}".format(address=self.address, user_id=self.user_id)


async def authentication_func(
    token: Token | None = Depends(optional_token), client: ClientInfo = Depends(client_details)
) -> RatelimitUser | None:
    if client is None:
        raise RuntimeError("Client is not provided")

    if token is None:
        return RatelimitUser(
            group="unknown",
            address=client.host,
        )

    return RatelimitUser(
        group=token.owner.role.name,
        address=client.host,
        user_id=token.owner.id,
    )


class MemoryRanking(BaseRanking):
    def __init__(self, user_model: type[T]):
        super().__init__(user_model)
        self.users: dict[UserID, T] = {}

    def clear(self):
        self.users.clear()

    async def save_user(self, authority: T):
        self.users[authority.unique_id] = authority

    async def get_user(self, authority_id: UserID) -> T:
        return self.users.get(authority_id)


class MemoryStore(BaseStore):
    def __init__(self):
        super().__init__()
        self.endpoints: dict[str, dict[str, Endpoint]] = {}
        self.user_endpoints: dict[UserID, dict[str, dict[str, Endpoint]]] = {}

    def clear(self):
        self.endpoints.clear()
        self.user_endpoints.clear()

    async def save_endpoint(self, endpoint: Endpoint) -> None:
        self.endpoints.setdefault(endpoint.path, {})[endpoint.method] = endpoint

    async def get_endpoint(self, path: str, method: str) -> Endpoint:
        endpoint = self.endpoints.get(path, {}).get(method)

        if endpoint is None:
            return Endpoint(path=path, method=method)

        return endpoint

    async def save_user_endpoint(self, endpoint: Endpoint, user: BaseUser) -> None:
        self.user_endpoints.setdefault(user.unique_id, {}).setdefault(endpoint.path, {})[
            endpoint.method
        ] = endpoint

    async def get_user_endpoint(self, path: str, method: str, user_id: UserID) -> Endpoint:
        endpoint = self.user_endpoints.get(user_id, {}).get(path, {}).get(method)

        if endpoint is None:
            return Endpoint(path=path, method=method)

        return endpoint


@lru_cache
def memory_ranking():
    return MemoryRanking(RatelimitUser)


@lru_cache
def memory_store():
    return MemoryStore()
