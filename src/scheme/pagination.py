from typing import TypeVar, Generic

from .model import SchemeModel


__all__ = ["Paginated"]


class PaginationData(SchemeModel):
    total: int
    pages: int
    page: int


T = TypeVar("T", bound=SchemeModel)


class Paginated(SchemeModel, Generic[T]):
    pagination: PaginationData
    items: list[T]
