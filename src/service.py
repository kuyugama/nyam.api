from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Token, User, Role


async def get_token(session: AsyncSession, body: str) -> Token | None:
    return await session.scalar(
        select(Token)
        .filter_by(body=body)
        .options(
            joinedload(Token.owner).options(joinedload(User.avatar), joinedload(User.role)),
        )
    )


async def get_default_role(session: AsyncSession) -> Role | None:
    return await session.scalar(select(Role).filter(Role.default))


async def get_role_by_name(session: AsyncSession, name: str) -> Role | None:
    return await session.scalar(select(Role).filter(Role.name == name))


async def get_user_by_nickname(session: AsyncSession, nickname: str) -> User | None:
    return await session.scalar(
        select(User)
        .filter_by(nickname=nickname)
        .options(joinedload(User.avatar), joinedload(User.role))
    )
