from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Query, File, UploadFile

from . import service
from src import permissions, constants
from .scheme import PublishTextPageBody
from src.database import acquire_session
from src.scheme import define_error_category
from ..composition.variant.dependencies import not_author
from src.service import get_next_index, update_next_indexes
from src.models import Chapter, Token, CompositionVariant, BasePage

from src.dependencies import (
    file_mime,
    master_grant,
    require_token,
    require_chapter,
    check_permissions,
)

define_error = define_error_category("content/page")
image_too_big = define_error("image-too-big", "Page image too big", 400)
mime_invalid = define_error("mime-invalid", "Invalid page image file type", 400)
type_invalid = define_error("type-invalid", "Invalid page type", 400)


async def chapter_composition_variant(
    chapter: Chapter = Depends(require_chapter),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.get_composition_variant(session, chapter.id)


@not_author.mark
async def validate_publish_image_permissions(
    author_token: Token = Depends(require_token),
    master_granted: bool = Depends(master_grant),
    variant: CompositionVariant = Depends(chapter_composition_variant),
):
    if variant.author_id != author_token.owner_id and not check_permissions(
        master_granted, author_token, permissions.override_author
    ):
        raise not_author


@type_invalid.mark
async def validate_publish_text_page(
    body: PublishTextPageBody,
    chapter: Chapter = Depends(require_chapter),
    session: AsyncSession = Depends(acquire_session),
    variant: CompositionVariant = Depends(chapter_composition_variant),
):
    if constants.COMPOSITION_STYLE_TO_PAGE_TYPE[variant.origin.style] != constants.PAGE_TEXT:
        raise type_invalid

    if body.index is None:
        body.index = await get_next_index(session, BasePage, BasePage.chapter_id == chapter.id)
    else:
        await update_next_indexes(session, BasePage, BasePage.chapter_id == chapter.id, body.index)

    return body


async def validate_image_page_index(
    index: int | None = Query(
        None,
        description="Порядковий номер сторінки, необов'язкове значення, "
        "якщо не вказано створиться автоматично",
    ),
    chapter: Chapter = Depends(require_chapter),
    session: AsyncSession = Depends(acquire_session),
):
    if index is None:
        index = await get_next_index(session, BasePage, BasePage.chapter_id == chapter.id)
    else:
        await update_next_indexes(session, BasePage, BasePage.chapter_id == chapter.id, index)

    return index


@image_too_big.mark
@mime_invalid.mark
@type_invalid.mark
async def validate_image_page_file(
    file: UploadFile = File(description="Зображення сторінки"),
    mime: str = Depends(file_mime),
    variant: CompositionVariant = Depends(chapter_composition_variant),
):
    if constants.COMPOSITION_STYLE_TO_PAGE_TYPE[variant.origin.style] != constants.PAGE_IMAGE:
        raise type_invalid

    if file.size > constants.PAGE_MAX_SIZE:
        raise image_too_big

    if mime not in constants.PAGE_ALLOWED_MIMES:
        raise mime_invalid

    return file
