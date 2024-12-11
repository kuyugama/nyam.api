from sqlalchemy import ForeignKey, event, Connection
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ..base import Base
from src import constants
from .chapter import Chapter
from ..image import UploadImage
from ..mixins import OwnedByTeamMixin
from src.util import update_within_flush_event


class BasePage(Base, OwnedByTeamMixin):
    __tablename__ = "service_pages"
    __mapper_args__ = {
        "polymorphic_identity": "default",
        "polymorphic_on": "type",
    }
    type: Mapped[str] = mapped_column(index=True)

    chapter_id = mapped_column(ForeignKey(Chapter.id, ondelete="CASCADE"))
    chapter: Mapped[Chapter] = relationship(foreign_keys=[chapter_id])

    image_id = mapped_column(ForeignKey(UploadImage.id), nullable=True)
    text: Mapped[str] = mapped_column(nullable=True)

    index: Mapped[int] = mapped_column(index=True)


class ImagePage(BasePage):
    __mapper_args__ = {"polymorphic_identity": constants.PAGE_IMAGE}
    image: Mapped[UploadImage] = relationship(foreign_keys=[BasePage.image_id])


class TextPage(BasePage):
    __mapper_args__ = {"polymorphic_identity": constants.PAGE_TEXT}


@event.listens_for(ImagePage, "before_insert")
@event.listens_for(TextPage, "before_insert")
def _new_page(_: type[BasePage], connection: Connection, page: BasePage):
    update_within_flush_event(page.chapter, connection, pages=page.chapter.pages + 1)


@event.listens_for(ImagePage, "before_delete")
@event.listens_for(TextPage, "before_delete")
def _remove_page(_: type[BasePage], connection: Connection, page: BasePage):
    update_within_flush_event(page.chapter, connection, pages=page.chapter.pages - 1)
