from sqlalchemy import ForeignKey, event, Connection
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ..base import Base
from .volume import Volume
from .composition import CompositionVariant
from src.util import update_within_flush_event, update_by_pk


class Chapter(Base):
    volume_id = mapped_column(ForeignKey(Volume.id, ondelete="CASCADE"))
    volume: Mapped[Volume] = relationship(foreign_keys=[volume_id])

    index: Mapped[int] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(index=True, nullable=True)

    # Cached fields
    pages: Mapped[int] = mapped_column(index=True, default=0)

    @property
    def computed_title(self) -> str:
        """
        return {{index}} if title is null or empty string else "{{index}} | {{title}}"
        """
        return str(self.index) if not self.title else f"{self.index} | {self.title}"


@event.listens_for(Chapter, "before_insert")
def _new_chapter(_: type[Chapter], connection: Connection, chapter: Chapter):
    update_within_flush_event(chapter.volume, connection, chapters=chapter.volume.chapters + 1)

    connection.execute(
        update_by_pk(
            CompositionVariant, chapter.volume.variant_id, chapters=CompositionVariant.chapters + 1
        )
    )


@event.listens_for(Chapter, "before_delete")
def _remove_chapter(_: type[Chapter], connection: Connection, chapter: Chapter):
    update_within_flush_event(chapter.volume, connection, chapters=chapter.volume.chapters + 1)

    connection.execute(
        update_by_pk(
            CompositionVariant, chapter.volume.variant_id, chapters=CompositionVariant.chapters - 1
        )
    )
