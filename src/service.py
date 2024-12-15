from datetime import timedelta
from typing import Any

from sqlalchemy import select, delete, func, update, Select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.util import now
from src import constants
from src.models import (
    Team,
    Role,
    User,
    Token,
    Volume,
    Chapter,
    BasePage,
    TextPage,
    ImagePage,
    TeamMember,
    Composition,
    CompositionVariant,
)


IMAGE_TYPE_TO_MODEL = {
    constants.PAGE_TEXT: TextPage,
    constants.PAGE_IMAGE: ImagePage,
}


def variant_options(select: Select) -> Select:
    member_load = joinedload(CompositionVariant.member).options(
        joinedload(TeamMember.user).options(joinedload(User.avatar), joinedload(User.role)),
        joinedload(TeamMember.role),
    )
    # TODO: Add loading team logo when this feature is added
    team_load = joinedload(CompositionVariant.team)

    origin_load = joinedload(CompositionVariant.origin).options(
        joinedload(Composition.preview), selectinload(Composition.genres)
    )
    return select.options(member_load, team_load, origin_load)


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
    return await session.scalar(
        select(Role).filter_by(team_member_role=False).order_by(Role.weight.asc()).limit(1)
    )


async def get_team_default_role(session: AsyncSession) -> Role | None:
    return await session.scalar(
        select(Role).filter_by(team_member_role=True).order_by(Role.weight.asc()).limit(1)
    )


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
    return await session.scalar(
        variant_options(select(CompositionVariant).filter_by(id=variant_id))
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


async def get_page(session: AsyncSession, page_id: int) -> TextPage | ImagePage | None:
    style = await session.scalar(
        select(Composition.style).filter(
            Composition.id == CompositionVariant.origin_id,  # type: ignore
            CompositionVariant.id == Volume.variant_id,  # type: ignore
            Volume.id == Chapter.volume_id,  # type: ignore
            Chapter.id == BasePage.chapter_id,  # type: ignore
            BasePage.id == page_id,  # type: ignore
        )
    )

    if not style:
        return None

    model = IMAGE_TYPE_TO_MODEL[constants.COMPOSITION_STYLE_TO_PAGE_TYPE[style]]

    options = ()
    if model is ImagePage:
        options = (joinedload(ImagePage.image),)

    return await session.scalar(select(model).filter(model.id == page_id).options(*options))  # type: ignore


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


async def get_team(session: AsyncSession, team_id: int) -> Team:
    return await session.scalar(select(Team).filter_by(id=team_id))


async def get_team_member(session: AsyncSession, team_id: int, user_id: int) -> TeamMember:
    return await session.scalar(
        select(TeamMember)
        .filter_by(team_id=team_id, user_id=user_id)
        .options(joinedload(TeamMember.role), joinedload(TeamMember.team))
    )
