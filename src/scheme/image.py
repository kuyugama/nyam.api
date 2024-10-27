from .model import Object


class UploadImage(Object):
    url: str
    width: int
    height: int
    mimetype: str
