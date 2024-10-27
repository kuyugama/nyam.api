from datetime import datetime

import sqlalchemy.orm
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from src.util import now, camel_to_snake


class Base(AsyncAttrs, DeclarativeBase):

    def __init_subclass__(cls, **kwargs):

        if not hasattr(cls, "__tablename__"):
            name = camel_to_snake(cls.__qualname__)

            cls.__tablename__ = "service_" + name + "s"

        super().__init_subclass__(**kwargs)

    id: sa.orm.Mapped[int] = sa.orm.mapped_column(sa.BIGINT, primary_key=True, index=True)

    created_at: sa.orm.Mapped[datetime] = sa.orm.mapped_column(default=now, index=True)
    updated_at: sa.orm.Mapped[datetime] = sa.orm.mapped_column(
        default=None, nullable=True, onupdate=now, index=True
    )
