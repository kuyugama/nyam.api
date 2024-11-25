from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from . import User
from .base import Base


class OAuthIdentity(Base):
    __tablename__ = "service_oauth_identities"
    user_id = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    user: Mapped[User] = relationship(foreign_keys=[user_id])

    provider: Mapped[str] = mapped_column(index=True)
    # Serialized user identifier on provider's resource
    provider_user: Mapped[str] = mapped_column(index=True)
