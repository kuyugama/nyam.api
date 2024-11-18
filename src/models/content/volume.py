from sqlalchemy import ForeignKey, event, Connection
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import update

from ..base import Base
from .composition import CompositionVariant


class Volume(Base):
    variant_id = mapped_column(ForeignKey(CompositionVariant.id, ondelete="CASCADE"))
    variant: Mapped[CompositionVariant] = relationship(foreign_keys=[variant_id])

    index: Mapped[int] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(index=True, nullable=True)

    # Cached fields
    chapters: Mapped[int] = mapped_column(index=True, default=0)

    @property
    def computed_title(self) -> str:
        """
        return {{index}} if title is null or empty string else "{{index}} | {{title}}"
        """
        return str(self.index) if not self.title else f"{self.index} | {self.title}"


@event.listens_for(Volume, "before_insert")
def _new_volume(_: type[Volume], connection: Connection, volume: Volume):
    volume.variant.volumes += 1
    connection.execute(
        update(CompositionVariant)
        .values(volumes=volume.variant.volumes)
        .filter_by(id=volume.variant_id)
    )


@event.listens_for(Volume, "before_delete")
def _remove_volume(_: type[Volume], connection: Connection, volume: Volume):
    volume.variant.volumes -= 1
    connection.execute(
        update(CompositionVariant)
        .values(volumes=volume.variant.volumes)
        .filter_by(id=volume.variant_id)
    )
