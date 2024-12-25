import sys
import copy
import inspect
import hashlib
import secrets
from pathlib import Path
from typing import Any, Sequence
from datetime import timedelta, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src import util, constants
from src.util import now, secure_hash
from src.permissions import permissions
from src.util.permissions_util import Permission, generate_permission

from src.models import (
    User,
    Role,
    Token,
    Genre,
    Volume,
    Chapter,
    TextPage,
    ImagePage,
    UploadImage,
    Composition,
    CompositionVariant,
    Team,
    TeamMember,
)


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
    permissions_: dict[str, bool] = None,
    team_member_role: bool = False,
) -> Role:
    if permissions_ is None:
        permissions_ = {
            permissions.user.own.update_info: True,
        }

    role = Role(
        name=name,
        title=title,
        weight=weight,
        default=default,
        permissions=permissions_to_json(permissions_),
        team_member_role=team_member_role,
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


async def create_team(session: AsyncSession, name: str = "team", description: str = "team") -> Team:
    team = Team(
        name=name,
        description=description,
    )

    session.add(team)
    await session.commit()

    return team


async def create_team_member(
    session: AsyncSession, member: User, team: Team, role: Role, pseudonym: str = "Team member"
) -> TeamMember:
    team_member = TeamMember(
        pseudonym=pseudonym,
        user=member,
        team=team,
        role=role,
    )

    session.add(team_member)
    await session.commit()

    return team_member


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
) -> Composition:
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
    team: Team,
    team_member: TeamMember,
    title: str = None,
    synopsis: str | None = None,
) -> CompositionVariant:
    variant = CompositionVariant(
        origin=origin,
        title_local=title,
        synopsis_local=synopsis,
        status=constants.STATUS_COMPOSITION_VARIANT_PENDING,
        team=team,
        member=team_member,
    )

    session.add(variant)

    await session.commit()

    return variant


async def create_genre(
    session: AsyncSession, name_en: str = "Drama", name_uk: str = "Драма", slug: str = "drama"
) -> Genre:
    genre = Genre(name_uk=name_uk, name_en=name_en, slug=slug)

    session.add(genre)

    await session.commit()

    return genre


async def create_volume(
    session: AsyncSession,
    team_member: TeamMember,
    composition_variant: CompositionVariant,
    index: int,
    title: str = None,
) -> Volume:
    volume = Volume(
        variant=composition_variant,
        team=team_member.team,
        member=team_member,
        title=title,
        index=index,
    )

    session.add(volume)

    await session.commit()

    return volume


async def create_chapter(
    session: AsyncSession, team_member: TeamMember, volume: Volume, index: int, title: str = None
) -> Chapter:
    chapter = Chapter(
        volume=volume,
        team=team_member.team,
        member=team_member,
        title=title,
        index=index,
    )

    session.add(chapter)

    await session.commit()

    return chapter


async def create_text_page(
    session: AsyncSession, team_member: TeamMember, chapter: Chapter, index: int, text: str
) -> TextPage:
    page = TextPage(
        chapter=chapter,
        team=team_member.team,
        member=team_member,
        index=index,
        text=text,
    )

    session.add(page)

    await session.commit()

    return page


async def create_image_page(
    session: AsyncSession, team_member: TeamMember, chapter: Chapter, index: int, image: UploadImage
) -> ImagePage:
    page = ImagePage(
        chapter=chapter, team=team_member.team, member=team_member, index=index, image=image
    )

    session.add(page)

    await session.commit()

    return page


async def create_upload_image(session: AsyncSession) -> UploadImage:
    image = UploadImage(
        url="https://example.com/image.png",
        width=720,
        height=480,
        mime_type="image/png",
        key="example_upload/image.png",
    )

    session.add(image)

    await session.commit()

    return image


def assert_contain(
    source: dict[str, Any],
    recursive: bool = False,
    __frame=None,
    __rel_path=None,
    __name: str = "",
    **kw,
):
    frame = inspect.stack()[1]
    file_path = Path(frame.filename)
    rel_path = file_path.relative_to(sys.path[0])

    if recursive:
        frame = __frame or frame
        rel_path = __rel_path or rel_path

    for name, value in kw.items():
        if __name:
            name_ = __name + " -> " + name
        else:
            name_ = name

        actual_value = source.get(name)
        if recursive and isinstance(actual_value, dict) and isinstance(value, dict):
            assert_contain(
                actual_value,
                recursive=True,
                __frame=frame,
                __rel_path=rel_path,
                __name=name_,
                **value,
            )
            continue

        if actual_value != value:

            print(
                f"{rel_path}:{frame.lineno} => {frame.function}",
                f"  {name_} => {actual_value!r} != {value!r}",
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


def email_to_nickname(email: str) -> str:
    source = email.split("@")[0]

    string = ""
    for char in source:
        if char in ".-+":
            if not string.endswith("_"):
                string += "_"
            continue

        string += char

    if len(string) < constants.USER_NICKNAME_MIN:
        string += secrets.token_hex(constants.USER_NICKNAME_MIN - len(string))

    return string


def permissions_to_json(
    permissions: (
        dict[str | tuple[str, ...] | Permission, bool]
        | Sequence[str | tuple[str, ...] | Permission]
        | None
    )
) -> dict[str, bool] | list[str] | None:
    if permissions is None:
        return permissions

    if isinstance(permissions, dict):
        result = {}
        for permission, allowed in permissions.items():
            if isinstance(permission, tuple):
                permission = generate_permission(permission, ())

            result[str(permission)] = allowed

        return result

    result = []
    for permission in permissions:
        if isinstance(permission, tuple):
            permission = generate_permission(permission, ())

        result.append(permission)

    return result
