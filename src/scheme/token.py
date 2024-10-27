from .user import FullUser
from .model import SchemeModel, Object, datetime_pd


class Token(SchemeModel):
    expire_at: datetime_pd
    used_at: datetime_pd | None
    token: str


class FullToken(Object, Token):
    owner: FullUser
