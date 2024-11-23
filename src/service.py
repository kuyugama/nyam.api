from datetime import timedelta
from typing import Any

from sqlalchemy import select, delete, func, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Token, User, Role, CompositionVariant, Composition, Volume, Chapter, BasePage
from src.util import now


async def get_token(session: AsyncSession, body: str) -> Token | None:
    return await session.scalar(
        select(Token)
        .filter_by(body=body)
        .options(
            joinedload(Token.owner).options(joinedload(User.avatar), joinedload(User.role)),
        )
    )


async def drop_expired_tokens(session: AsyncSession, shift: timedelta = timedelta(days=2)) -> None:
    await session.execute(delete(Token).filter(Token.expire_at <= (now() - abs(shift))))
    await session.commit()


async def get_default_role(session: AsyncSession) -> Role | None:
    return await session.scalar(select(Role).filter(Role.default))


async def get_role_by_name(session: AsyncSession, name: str) -> Role | None:
    return await session.scalar(select(Role).filter(Role.name == name))


async def get_role_by_weight(session: AsyncSession, weight: int) -> Role | None:
    return await session.scalar(select(Role).filter(Role.weight == weight))


async def get_user_by_nickname(session: AsyncSession, nickname: str) -> User | None:
    return await session.scalar(
        select(User)
        .filter_by(nickname=nickname)
        .options(joinedload(User.avatar), joinedload(User.role))
    )


async def get_composition_variant(session: AsyncSession, variant_id: int) -> CompositionVariant:
    author_load = joinedload(CompositionVariant.author).options(
        joinedload(User.avatar), joinedload(User.role)
    )

    origin_load = joinedload(CompositionVariant.origin).options(
        joinedload(Composition.preview), selectinload(Composition.genres)
    )
    return await session.scalar(
        select(CompositionVariant).filter_by(id=variant_id).options(author_load, origin_load)
    )


async def get_composition_variant_by_chapter_id(
    session: AsyncSession, chapter_id: int
) -> CompositionVariant:
    return await session.scalar(
        select(CompositionVariant)
        .filter(
            CompositionVariant.id == Volume.variant_id,  # type: ignore
            Volume.id == Chapter.volume_id,  # type: ignore
            Chapter.id == chapter_id,  # type: ignore
        )
        .options(joinedload(CompositionVariant.origin))
    )


async def get_volume(session: AsyncSession, volume_id: int) -> Volume:
    return await session.scalar(select(Volume).filter_by(id=volume_id))


async def get_chapter(session: AsyncSession, chapter_id: int) -> Chapter:
    return await session.scalar(select(Chapter).filter_by(id=chapter_id))


async def get_next_index(
    session: AsyncSession, model: type[Volume | Chapter | BasePage], filter_: Any
) -> int:
    return await session.scalar(select(func.coalesce(func.max(model.index), 0) + 1).filter(filter_))


async def update_next_indexes(
    session: AsyncSession, model: type[Volume | Chapter | BasePage], filter_: Any, start_index: int
):
    await session.execute(
        update(model)
        .values(
            index=model.index + 1,
        )
        .filter(model.index >= start_index, filter_),
    )
