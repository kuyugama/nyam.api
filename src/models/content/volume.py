from sqlalchemy import ForeignKey, event, Connection
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ..base import Base
from ..mixins import OwnedByTeamMixin
from .composition import CompositionVariant
from src.util import update_within_flush_event


class Volume(Base, OwnedByTeamMixin):
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
    update_within_flush_event(volume.variant, connection, volumes=volume.variant.volumes + 1)


@event.listens_for(Volume, "before_delete")
def _remove_volume(_: type[Volume], connection: Connection, volume: Volume):
    update_within_flush_event(volume.variant, connection, volumes=volume.variant.volumes - 1)
