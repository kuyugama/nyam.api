from sqlalchemy import orm

from .base import Base


class Team(Base):
    __tablename__ = "service_teams"

    name: orm.Mapped[str] = orm.mapped_column(index=True)
    description: orm.Mapped[str] = orm.mapped_column(index=True)

    # Cached fields
    members: orm.Mapped[int] = orm.mapped_column(default=0, index=True)
    variants: orm.Mapped[int] = orm.mapped_column(default=0, index=True)
    rating: orm.Mapped[int] = orm.mapped_column(default=0, index=True)
    rated_by: orm.Mapped[int] = orm.mapped_column(default=0, index=True)
