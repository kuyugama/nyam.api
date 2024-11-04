from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models import Composition, UploadImage
from src.content_providers import ContentProviderComposition


async def get_composition_by_slug(session: AsyncSession, slug: str) -> Composition:
    return await session.scalar(
        select(Composition)
        .filter(Composition.slug == slug)
        .options(joinedload(Composition.preview))
    )


async def publish_composition_from_provider(
    session: AsyncSession, composition_: ContentProviderComposition
):
    preview = UploadImage(
        url=composition_.preview.url,
        width=composition_.preview.width,
        height=composition_.preview.height,
        mime_type=composition_.preview.mimetype,
    )

    composition = Composition(
        preview=preview,
        slug=composition_.slug,
        style=composition_.style,
        title_original=composition_.title_original,
        title_en=composition_.title_en,
        title_uk=composition_.title_uk,
        synopsis_en=composition_.synopsis_en,
        synopsis_uk=composition_.synopsis_uk,
        status=composition_.status,
        year=composition_.year,
        start_date=composition_.start_date and composition_.start_date.replace(tzinfo=None),
        nsfw=composition_.nsfw,
        genres=composition_.genres,
        tags=composition_.tags,
        chapters=composition_.chapters,
        volumes=composition_.volumes,
        mal_id=composition_.mal_id,
        provider=composition_.provider,
        provider_id=composition_.provider_id,
    )

    session.add_all([preview, composition])
    await session.commit()

    return composition
