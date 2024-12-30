import secrets
from datetime import timedelta

import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from .scheme import SignUpBody
from src import constants
from src.models import User, Token
from src.util import secure_hash, now
from src.service import get_lowest_role, get_user_by_nickname

__all__ = [
    "create_user",
    "create_token",
    "get_user_by_email",
    "get_user_by_nickname",
]


async def create_user(session: AsyncSession, body: SignUpBody) -> User:
    user = User(
        email=body.email,
        nickname=body.nickname,
        password_hash=secure_hash(body.password),
        role=await get_lowest_role(session),
    )
    session.add(user)
    await session.commit()

    return user


async def create_token(session: AsyncSession, user: User) -> Token:
    token = Token(
        owner_id=user.id,
        expire_at=now() + timedelta(seconds=constants.TOKEN_TTL),
        body=secrets.token_hex(64),
    )
    session.add(token)
    await session.commit()

    return token


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(
        sa.select(User).filter_by(email=email).options(joinedload(User.avatar))
    )
