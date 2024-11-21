from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, select, func, ScalarResult

from .scheme import CreateVolumeBody
from src.models import CompositionVariant, Composition, User, Volume


def variants_filter(query: Select, slug: str) -> Select:
    return query.filter(
        CompositionVariant.origin_id == Composition.id,
        Composition.slug == slug,
    )


def variants_options(query: Select) -> Select:
    author_load = joinedload(CompositionVariant.author).options(
        joinedload(User.avatar), joinedload(User.role)
    )

    origin_load = joinedload(CompositionVariant.origin).joinedload(Composition.preview)

    return query.options(
        author_load,
        origin_load,
    )


async def count_variants(session: AsyncSession, slug: str) -> int:
    return await session.scalar(
        select(
            Composition.variants
        ).filter(
            Composition.slug == slug
        )
    )


async def list_variants(
    session: AsyncSession, slug: str, offset: int, limit: int
) -> ScalarResult[CompositionVariant]:
    return await session.scalars(
        variants_options(
            variants_filter(select(CompositionVariant).limit(limit).offset(offset), slug)
        )
    )


async def create_volume(
    session: AsyncSession, variant: CompositionVariant, body: CreateVolumeBody
) -> Volume:

    volume = Volume(
        variant=variant,
        index=body.index,
        title=body.title,
    )

    session.add(volume)

    await session.commit()

    return volume
