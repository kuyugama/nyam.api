from pydantic import Field

from src import constants
from .model import Object
from .image import UploadImage


class BasePage(Object):
    index: int = Field(description="Порядковий номер цієї сторінки")

    type: str = Field(
        description="Тип сторінки: text / image",
        examples=[constants.PAGE_TEXT, constants.PAGE_IMAGE],
    )

    chapter_id: int = Field(description="ID розділу")


class TextPage(BasePage):
    text: str = Field(description="Вміст сторінки")


class ImagePage(BasePage):
    image: UploadImage = Field(description="Вміст сторінки")
