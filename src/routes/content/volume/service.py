from sqlalchemy import Select, select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from .scheme import CreateChapterBody
from src.models import Volume, Chapter, TeamMember


def volume_filters(query: Select, variant_id: int):
    return query.filter(Volume.variant_id == variant_id)


def volume_options(query: Select):
    return query


async def list_volumes(
    session: AsyncSession, variant_id: int, offset: int, limit: int
) -> ScalarResult[Volume]:
    return await session.scalars(
        volume_filters(
            volume_options(select(Volume).order_by(Volume.index).offset(offset).limit(limit)),
            variant_id,
        )
    )


async def create_chapter(
    session: AsyncSession, volume: Volume, body: CreateChapterBody, team_member: TeamMember
):
    chapter = Chapter(
        volume=volume,
        index=body.index,
        title=body.title,
        team_id=volume.team_id,
        member_id=team_member.id,
    )

    session.add(chapter)

    await session.commit()

    return chapter
