from functools import lru_cache

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Table, Column, ForeignKey

from .base import Base


@lru_cache
def associate_tables(
    first: DeclarativeBase | str, second: DeclarativeBase | str, association_name: str
):
    if isinstance(first, DeclarativeBase):
        first = getattr(first, "id")

    if isinstance(second, DeclarativeBase):
        second = getattr(second, "id")

    return Table(
        f"association_{association_name}",
        Base.metadata,
        Column("first_id", ForeignKey(first, ondelete="CASCADE"), primary_key=True),
        Column("second_id", ForeignKey(second, ondelete="CASCADE"), primary_key=True),
    )


composition_genres = associate_tables(
    "service_genres.id", "service_compositions.id", "composition_genres"
)
