from sqlalchemy import ForeignKey, event, Connection, update
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ..base import Base
from .volume import Volume
from .composition import CompositionVariant


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
    chapter.volume.chapters += 1

    connection.execute(
        update(Volume).values(chapters=chapter.volume.chapters).filter_by(id=chapter.volume_id)
    )
    connection.execute(
        update(CompositionVariant)
        .values(chapters=CompositionVariant.chapters + 1)
        .filter_by(id=chapter.volume.variant_id)
    )


@event.listens_for(Chapter, "before_delete")
def _remove_chapter(_: type[Chapter], connection: Connection, chapter: Chapter):
    chapter.volume.chapters -= 1

    connection.execute(
        update(Volume).values(chapters=chapter.volume.chapters).filter_by(id=chapter.volume_id)
    )
    connection.execute(
        update(CompositionVariant)
        .values(chapters=CompositionVariant.chapters + 1)
        .filter_by(id=chapter.volume.variant_id)
    )
