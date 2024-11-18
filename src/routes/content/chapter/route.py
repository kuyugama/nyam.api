from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Chapter
from . import service
from src import scheme
from src.database import acquire_session
from src.dependencies import require_page, require_chapter, file_mime
from src.util import get_offset_and_limit, paginated_response
from .dependencies import (
    validate_publish_text_page,
    validate_publish_image_page,
    validate_image_page_index,
    validate_publish_image_permissions,
)
from .scheme import PublishTextPageBody

router = APIRouter(prefix="/chapter")


@router.get(
    "/list/{volume_id}",
    summary="Отримати розділи тому твору",
    operation_id="list_chapters",
    response_model=scheme.Paginated[scheme.Chapter],
)
async def list_chapters(
    volume_id: int,
    page: int = Depends(require_page),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    total = await service.count_chapters(session, volume_id)
    items = await service.list_chapters(session, volume_id, offset, limit)

    return paginated_response(items.all(), total, page, limit)


@router.get(
    "/{chapter_id}",
    summary="Отримати розділ",
    operation_id="get_chapter",
    response_model=scheme.Chapter,
)
async def get_chapter(chapter: Chapter = Depends(require_chapter)):
    return chapter


@router.post(
    "/{chapter_id}/page/text",
    summary="Опублікувати текстову сторінку до розділу",
    operation_id="publish_text_page",
    response_model=scheme.TextPage,
    dependencies=[Depends(validate_publish_image_permissions)],
)
async def publish_text_page(
    body: PublishTextPageBody = Depends(validate_publish_text_page),
    session: AsyncSession = Depends(acquire_session),
    chapter: Chapter = Depends(require_chapter),
):
    return await service.create_text_page(session, chapter, body)


@router.post(
    "/{chapter_id}/page/image",
    summary="Опублікувати сторінку із зображення до розділу",
    operation_id="publish_image_page",
    response_model=scheme.ImagePage,
    dependencies=[Depends(validate_publish_image_permissions)],
)
async def publish_image_page(
    image: UploadFile = Depends(validate_publish_image_page),
    session: AsyncSession = Depends(acquire_session),
    index: int = Depends(validate_image_page_index),
    chapter: Chapter = Depends(require_chapter),
    mime: str = Depends(file_mime),
):
    return await service.create_image_page(session, chapter, index, image, mime)
