import sys
import copy
import inspect
import hashlib
import secrets
from typing import Any
from pathlib import Path
from datetime import timedelta, datetime

from sqlalchemy.ext.asyncio import AsyncSession

import src
import src.permissions
from src import util, constants
from src.util import now, secure_hash
from src.models import User, Token, Role, Composition, Genre, CompositionVariant


class MockedResponse:
    def __init__(self, data: dict):
        self.data = copy.deepcopy(data)

    async def json(self):
        return self.data


async def create_role(
    session: AsyncSession,
    name: str,
    weight: int,
    default: bool = False,
    title: str = "Title",
    permissions: dict[str, bool] = None,
) -> Role:
    if permissions is None:
        permissions = {
            src.permissions.user.own.update_info: True,
        }

    role = Role(
        name=name,
        title=title,
        weight=weight,
        default=default,
        permissions=permissions,
    )
    session.add(role)

    await session.commit()

    return role


async def create_user(
    session: AsyncSession,
    email: str,
    nickname: str,
    role: Role,
    password: str | None = None,
    password_hash: str | None = None,
) -> User:
    if password is None and password_hash is None:
        raise ValueError("Either password or password_hash must be provided")

    if password is not None:
        password_hash = secure_hash(password)

    user = User(
        email=email,
        nickname=nickname,
        password_hash=password_hash,
        role=role,
    )

    session.add(user)
    await session.commit()

    return user


async def create_token(
    session: AsyncSession, user: User, valid_for: timedelta = timedelta(hours=6)
) -> Token:
    token = Token(
        owner_id=user.id,
        expire_at=now() + valid_for,
        body=secrets.token_hex(64),
    )
    session.add(token)
    await session.commit()

    return token


async def create_composition(
    session: AsyncSession,
    title_original: str = "World Trigger | Season 3",
    title_en: str | None = None,
    title_uk: str | None = None,
    synopsis_en: str | None = None,
    synopsis_uk: str | None = None,
    status: str = constants.STATUS_COMPOSITION_COMPLETED,
    year: int | None = 2000,
    start_date: datetime | None = None,
    nsfw: bool = False,
    genres: list[dict] | None = None,
    tags: list[str] | None = None,
    chapters: int | None = None,
    volumes: int | None = None,
    mal_id: int | None = None,
    style: str = constants.STYLE_COMPOSITION_MANGA,
):
    if genres is None:
        genres = []

    if tags is None:
        tags = []

    ref = hashlib.sha256(title_original.encode()).hexdigest()
    slug = util.slugify(title_original, ref)

    composition = Composition(
        slug=slug,
        title_original=title_original,
        title_en=title_en,
        title_uk=title_uk,
        synopsis_en=synopsis_en,
        synopsis_uk=synopsis_uk,
        status=status,
        year=year,
        start_date=start_date,
        nsfw=nsfw,
        genres=genres,
        tags=tags,
        chapters=chapters,
        volumes=volumes,
        mal_id=mal_id,
        provider=None,  # type: ignore
        provider_id=None,  # type: ignore
        style=style,
    )

    session.add(composition)

    await session.commit()

    return composition


async def create_composition_variant(
    session: AsyncSession,
    origin: Composition,
    author: User,
    title: str = None,
    synopsis: str | None = None,
):
    variant = CompositionVariant(
        origin=origin,
        title_local=title,
        synopsis_local=synopsis,
        status=constants.STATUS_COMPOSITION_VARIANT_PENDING,
        author=author,
    )

    session.add(variant)

    await session.commit()

    return variant


async def create_genre(
    session: AsyncSession, name_en: str = "Drama", name_uk: str = "Драма", slug: str = "drama"
):
    genre = Genre(name_uk=name_uk, name_en=name_en, slug=slug)

    session.add(genre)

    await session.commit()

    return genre


def assert_contain(source: dict[str, Any], **kw):
    for name, value in kw.items():
        actual_value = source.get(name)
        if actual_value != value:
            frame = inspect.stack()[1]
            file_path = Path(frame.filename)
            rel_path = file_path.relative_to(sys.path[0])
            print(
                f"{rel_path}:{frame.lineno} => {frame.function}",
                f"  {name} -> {actual_value!r} != {value!r}",
                sep="\n",
            )
        assert actual_value == value


def assert_composition(source: dict[str, Any], composition: Composition):
    assert_contain(
        source,
        title_uk=composition.title_uk,
        title_en=composition.title_en,
        title_original=composition.title_original,
        title=composition.title,
        synopsis_uk=composition.synopsis_uk,
        synopsis_en=composition.synopsis_en,
        synopsis=composition.synopsis,
        genres=[
            {
                "name_uk": genre.name_uk,
                "name_en": genre.name_en,
                "slug": genre.slug,
            }
            for genre in composition.genres
        ],
        tags=composition.tags,
        nsfw=composition.nsfw,
        mal_id=composition.mal_id,
        provider=composition.provider,
        provider_id=composition.provider_id,
        style=composition.style,
        score=composition.score,
        scored_by=composition.scored_by,
        chapters=composition.chapters,
        volumes=composition.volumes,
        variants=composition.variants,
        id=composition.id,
    )
