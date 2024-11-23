from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select, func, ScalarResult

from src import constants
from src.content_providers import ContentProviderComposition
from .scheme import CreateCompositionVariantBody, CompositionListBody
from src.models import Composition, UploadImage, CompositionVariant, User, Genre


async def get_composition_by_slug(session: AsyncSession, slug: str) -> Composition:
    return await session.scalar(
        select(Composition)
        .filter(Composition.slug == slug)
        .options(joinedload(Composition.preview), selectinload(Composition.genres))
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

    genres = (
        await session.scalars(
            select(Genre).filter(Genre.slug.in_([genre["slug"] for genre in composition_.genres]))
        )
    ).all()

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
        tags=composition_.tags,
        genres=[],
        chapters=composition_.chapters,
        volumes=composition_.volumes,
        mal_id=composition_.mal_id,
        provider=composition_.provider,
        provider_id=composition_.provider_id,
    )

    composition.genres.extend(genres)

    session.add_all([preview, composition])
    await session.commit()

    return composition


async def publish_composition_variant(
    session: AsyncSession, origin: Composition, body: CreateCompositionVariantBody, author: User
) -> CompositionVariant:
    variant = CompositionVariant(
        origin=origin,
        author=author,
        status=constants.STATUS_COMPOSITION_VARIANT_PENDING,
        title_local=body.title,
        synopsis_local=body.synopsis,
    )

    session.add(variant)

    await session.commit()

    return variant


def compositions_filters(query: Select, body: CompositionListBody):
    if body.genres is not None:
        query = query.filter(*(Composition.genres.any(Genre.slug == slug) for slug in body.genres))

    if body.genres_exclude is not None:
        query = query.filter(
            *(~Composition.genres.any(Genre.slug == slug) for slug in body.genres_exclude)
        )

    if body.tags is not None:
        query = query.filter(Composition.tags.op("@>")(body.tags))

    if body.tags_exclude is not None:
        query = query.filter(Composition.tags.op("<>")(body.tags_exclude))

    if body.nsfw is not None:
        query = query.filter(Composition.nsfw == body.nsfw)

    if body.years is not None:
        query = query.filter(
            Composition.year >= body.years[0],
            Composition.year <= body.years[1],
        )

    if body.chapters is not None:
        query = query.filter(
            Composition.chapters >= body.chapters[0],
            Composition.chapters <= body.chapters[1],
        )

    if body.volumes is not None:
        query = query.filter(
            Composition.volumes >= body.volumes[0],
            Composition.volumes <= body.volumes[1],
        )

    if body.styles is not None:
        query = query.filter(Composition.style.in_(body.styles))

    return query


def compositions_options(query: Select):
    return query.options(joinedload(Composition.preview), selectinload(Composition.genres))


async def count_compositions(session: AsyncSession, body: CompositionListBody) -> int:
    return await session.scalar(compositions_filters(select(func.count(Composition.id)), body))


async def list_compositions(
    session: AsyncSession, body: CompositionListBody, offset: int, limit: int
) -> ScalarResult[Composition]:
    return await session.scalars(
        compositions_options(
            compositions_filters(select(Composition).offset(offset).limit(limit), body)
        )
    )
