import sqlalchemy.orm as orm

from .base import Base


class UploadImage(Base):
    url: orm.Mapped[str]
    width: orm.Mapped[int]
    height: orm.Mapped[int]
    mime_type: orm.Mapped[str]

    key: orm.Mapped[str] = orm.mapped_column(nullable=True)

    @property
    def mimetype(self):
        return self.mime_type
