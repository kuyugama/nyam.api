from sqlalchemy import Select, select, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Volume, Chapter


def volume_filters(query: Select, variant_id: int):
    return query.filter(Volume.variant_id == variant_id)


def volume_options(query: Select):
    return query


async def count_volumes(session: AsyncSession, variant_id: int):
    return await session.scalar(volume_filters(select(func.count(Volume.id)), variant_id))


async def list_volumes(
    session: AsyncSession, variant_id: int, offset: int, limit: int
) -> ScalarResult[Volume]:
    return await session.scalars(
        volume_filters(volume_options(select(Volume).offset(offset).limit(limit)), variant_id)
    )


async def create_chapter(session: AsyncSession, volume: Volume, body):
    chapter = Chapter(
        volume=volume,
        index=body.index,
        title=body.title,
    )

    session.add(chapter)

    await session.commit()

    return chapter
