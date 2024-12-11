import mimetypes
import secrets

from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile
from sqlalchemy import Select, select, ScalarResult

from config import settings
from src.models import (
    Volume,
    Chapter,
    TextPage,
    ImagePage,
    UploadImage,
    CompositionVariant,
    TeamMember,
)
from src.routes.content.chapter.scheme import PublishTextPageBody

from src.scheme import APIError
from src.util import upload_file_obj
from src.service import get_composition_variant_by_chapter_id


def chapter_filters(query: Select, volume_id: int):
    return query.filter(Chapter.volume_id == volume_id)


def chapter_options(query: Select):
    return query


async def list_chapters(
    session: AsyncSession, volume_id: int, offset: int, limit: int
) -> ScalarResult[Volume]:
    return await session.scalars(
        chapter_filters(
            chapter_options(select(Chapter).order_by(Chapter.index).offset(offset).limit(limit)),
            volume_id,
        )
    )


async def create_text_page(
    session: AsyncSession, chapter: Chapter, body: PublishTextPageBody, team_member: TeamMember
):
    page = TextPage(
        chapter=chapter,
        index=body.index,
        text=body.text,
        team_id=chapter.team_id,
        member_id=team_member.id,
    )

    session.add(page)

    await session.commit()

    return page


async def get_composition_variant(session: AsyncSession, chapter_id: int) -> CompositionVariant:
    return await get_composition_variant_by_chapter_id(session, chapter_id)


async def create_image_page(
    session: AsyncSession,
    chapter: Chapter,
    index: int,
    image: UploadFile,
    mime: str,
    team_member: TeamMember,
) -> ImagePage:
    try:
        width, height = Image.open(image.file).size
        await image.seek(0)
    except Exception as e:
        raise APIError("users", "image-handling-error", extra={"message": e.args[0]})

    key = settings.cdn.key_format.page.format(
        chapter_id=chapter.id, hex=secrets.token_hex(16), ext=mimetypes.guess_extension(mime)
    )

    await upload_file_obj(image.file, key, mime)

    image = UploadImage(
        url=settings.cdn.url_format.format(key=key),
        width=width,
        height=height,
        mime_type=mime,
        key=key,
    )

    page = ImagePage(
        image=image, chapter=chapter, index=index, team_id=chapter.team_id, member_id=team_member.id
    )

    session.add_all([image, page])

    await session.commit()

    return page
