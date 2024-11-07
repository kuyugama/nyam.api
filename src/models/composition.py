from datetime import datetime

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy import String, ForeignKey, event, Connection
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import User
from .image import UploadImage


class Composition(Base):
    preview_id = mapped_column(ForeignKey(UploadImage.id, ondelete="SET NULL"), nullable=True)
    preview: Mapped[UploadImage] = relationship(UploadImage)

    slug: Mapped[str] = mapped_column(index=True)

    style: Mapped[str] = mapped_column(index=True)

    # Titles
    title_original: Mapped[str] = mapped_column(index=True)
    title_en: Mapped[str] = mapped_column(index=True, nullable=True)
    title_uk: Mapped[str] = mapped_column(index=True, nullable=True)

    # Synopses
    synopsis_en: Mapped[str] = mapped_column(index=True, nullable=True)
    synopsis_uk: Mapped[str] = mapped_column(index=True, nullable=True)

    # Other fields
    status: Mapped[str]
    year: Mapped[int] = mapped_column(index=True, nullable=True)
    start_date: Mapped[datetime] = mapped_column(index=True, nullable=True)
    nsfw: Mapped[bool] = mapped_column(index=True, default=False)
    genres: Mapped[list[dict]] = mapped_column(MutableList.as_mutable(JSONB))  # type: ignore
    tags: Mapped[list[str]] = mapped_column(ARRAY(String))
    chapters: Mapped[int] = mapped_column(index=True, nullable=True)
    volumes: Mapped[int] = mapped_column(index=True, nullable=True)

    # My Anime List id
    mal_id: Mapped[int] = mapped_column(index=True, nullable=True)

    # Content provider name
    provider: Mapped[str] = mapped_column(index=True, nullable=True)
    # Resource id at content provider
    provider_id: Mapped[str] = mapped_column(index=True, nullable=True)

    # Cached fields
    variants: Mapped[int] = mapped_column(default=0, index=True)
    score: Mapped[float] = mapped_column(default=0, index=True)
    scored_by: Mapped[int] = mapped_column(default=0, index=True)

    @property
    def title(self):
        return self.title_uk or self.title_en or self.title_original

    @property
    def synopsis(self):
        return self.synopsis_uk or self.synopsis_en


class CompositionVariant(Base):
    origin_id = mapped_column(ForeignKey(Composition.id, ondelete="CASCADE"))
    origin: Mapped[Composition] = relationship(foreign_keys=[origin_id])

    author_id = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    author: Mapped[User] = relationship(foreign_keys=[author_id])

    status: Mapped[str] = mapped_column(index=True)

    title_local: Mapped[str] = mapped_column(index=True, nullable=True)
    synopsis_local: Mapped[str] = mapped_column(index=True, nullable=True)

    # Cached fields
    chapters: Mapped[int] = mapped_column(index=True)
    volumes: Mapped[int] = mapped_column(index=True)

    @property
    def title(self) -> str | None:
        return self.title_local or self.origin.title

    @property
    def synopsis(self) -> str | None:
        return self.synopsis_local or self.origin.synopsis


@event.listens_for(CompositionVariant, "before_insert")
def _new_variant(_: type[CompositionVariant], __: Connection, target: CompositionVariant):
    target.origin.variants += 1


@event.listens_for(CompositionVariant, "before_delete")
def _new_variant(_: type[CompositionVariant], __: Connection, target: CompositionVariant):
    target.origin.variants -= 1
