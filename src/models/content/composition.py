from datetime import datetime

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, ForeignKey, event, Connection
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .genre import Genre
from .. import m2m_tables
from ..image import UploadImage
from ..mixins import OwnedByTeamMixin
from src.util import update_within_flush_event


class Composition(Base):
    __tablename__ = "service_compositions"

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
    genres: Mapped[list[Genre]] = relationship(secondary=m2m_tables.composition_genres)
    tags: Mapped[list[str]] = mapped_column(MutableList.as_mutable(ARRAY(String)))
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


class CompositionVariant(Base, OwnedByTeamMixin):
    __tablename__ = "service_composition_variants"

    origin_id = mapped_column(ForeignKey(Composition.id, ondelete="CASCADE"))
    origin: Mapped[Composition] = relationship(foreign_keys=[origin_id])

    status: Mapped[str] = mapped_column(index=True)

    title_local: Mapped[str] = mapped_column(index=True, nullable=True)
    synopsis_local: Mapped[str] = mapped_column(index=True, nullable=True)

    # Cached fields
    chapters: Mapped[int] = mapped_column(index=True, default=0)
    volumes: Mapped[int] = mapped_column(index=True, default=0)

    @property
    def title(self) -> str | None:
        return self.title_local or self.origin.title

    @property
    def synopsis(self) -> str | None:
        return self.synopsis_local or self.origin.synopsis


@event.listens_for(CompositionVariant, "before_insert")
def _new_variant(_: type[CompositionVariant], connection: Connection, variant: CompositionVariant):
    update_within_flush_event(variant.team, connection, variants=variant.team.variants + 1)
    update_within_flush_event(variant.member, connection, variants=variant.member.variants + 1)
    update_within_flush_event(variant.origin, connection, variants=variant.origin.variants + 1)


@event.listens_for(CompositionVariant, "before_delete")
def _remove_variant(
    _: type[CompositionVariant], connection: Connection, variant: CompositionVariant
):
    update_within_flush_event(variant.team, connection, variants=variant.team.variants - 1)
    update_within_flush_event(variant.member, connection, variants=variant.member.variants - 1)
    update_within_flush_event(variant.origin, connection, variants=variant.origin.variants - 1)
