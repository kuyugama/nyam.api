from sqlalchemy import orm
from sqlalchemy.testing.schema import mapped_column

from ..base import Base


class Genre(Base):
    __tablename__ = "service_genres"
    name_uk: orm.Mapped[str] = mapped_column()
    name_en: orm.Mapped[str] = mapped_column()
    slug: orm.Mapped[str] = mapped_column(index=True)
