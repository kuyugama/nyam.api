from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base
from .oauth_identity import OAuthIdentity


class ThirdpartyToken(Base):
    __tablename__ = "service_thirdparty_tokens"

    identity_id = mapped_column(ForeignKey(OAuthIdentity.id))
    identity: Mapped[OAuthIdentity] = relationship(foreign_keys=[identity_id])

    access_token: Mapped[str]
    token_type: Mapped[str | None] = mapped_column(nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(nullable=True)

    refresh_after: Mapped[datetime]
    refresh_before: Mapped[datetime]
