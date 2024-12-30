from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, select, ScalarResult

from .scheme import CreateVolumeBody
from src.service import variant_options
from src.models import CompositionVariant, Composition, Volume, TeamMember


def variants_filter(query: Select, slug: str) -> Select:
    return query.filter(
        CompositionVariant.origin_id == Composition.id,
        Composition.slug == slug,
    )


async def count_variants(session: AsyncSession, slug: str) -> int:
    return await session.scalar(select(Composition.variants).filter(Composition.slug == slug)) or 0


async def list_variants(
    session: AsyncSession, slug: str, offset: int, limit: int
) -> ScalarResult[CompositionVariant]:
    return await session.scalars(
        variant_options(
            variants_filter(select(CompositionVariant).limit(limit).offset(offset), slug)
        )
    )


async def create_volume(
    session: AsyncSession,
    variant: CompositionVariant,
    body: CreateVolumeBody,
    team_member: TeamMember,
) -> Volume:

    volume = Volume(
        variant=variant,
        index=body.index,
        title=body.title,
        team_id=variant.team_id,
        member_id=team_member.id,
    )

    session.add(volume)

    await session.commit()

    return volume
