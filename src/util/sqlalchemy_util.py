from functools import lru_cache
from typing import cast, Any, Mapping

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Update, update, Connection
from sqlalchemy.orm.attributes import set_committed_value


@lru_cache(maxsize=64)
def get_pk(
    model: type[DeclarativeBase], with_attr: bool = False
) -> None | Column | tuple[str, Column]:
    columns: Mapping[str, Column] = cast(Mapping[str, Column], model.__table__.columns)
    for attr, column in columns.items():
        if not column.primary_key:
            continue

        if with_attr:
            return attr, column

        return column


def update_by_pk(model: type[DeclarativeBase], pk_value: Any, **values) -> Update:
    return update(model).values(**values).filter(get_pk(model) == pk_value)


def update_within_flush_event(object_: DeclarativeBase, connection: Connection, **values) -> None:
    model = type(object_)
    pk_name, _ = get_pk(model, with_attr=True)
    pk_value = getattr(object_, pk_name)

    update_values: dict[str, Any] = {}
    for name, value in values.items():
        if not hasattr(object_, name):
            continue
        set_committed_value(object_, name, value)
        update_values[name] = value

    connection.execute(update_by_pk(model, pk_value, **update_values))
