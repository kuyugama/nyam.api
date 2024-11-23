from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Chapter, Volume
from . import service
from src import scheme, permissions
from src.database import acquire_session
from src.dependencies import (
    require_page,
    require_chapter,
    file_mime,
    require_volume,
    require_permissions,
)
from src.util import get_offset_and_limit, paginated_response
from .dependencies import (
    validate_publish_text_page,
    validate_image_page_file,
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
    volume: Volume = Depends(require_volume),
    page: int = Depends(require_page),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    items = await service.list_chapters(session, volume.id, offset, limit)

    return paginated_response(items.all(), volume.chapters, page, limit)


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
    dependencies=[
        Depends(validate_publish_image_permissions),
        require_permissions(permissions.page_text.create),
    ],
)
async def publish_text_page(
    chapter: Chapter = Depends(require_chapter),
    session: AsyncSession = Depends(acquire_session),
    body: PublishTextPageBody = Depends(validate_publish_text_page),
):
    return await service.create_text_page(session, chapter, body)


@router.post(
    "/{chapter_id}/page/image",
    summary="Опублікувати сторінку із зображення до розділу",
    operation_id="publish_image_page",
    response_model=scheme.ImagePage,
    dependencies=[
        Depends(validate_publish_image_permissions),
        require_permissions(permissions.page_image.create),
    ],
)
async def publish_image_page(
    mime: str = Depends(file_mime),
    chapter: Chapter = Depends(require_chapter),
    index: int = Depends(validate_image_page_index),
    session: AsyncSession = Depends(acquire_session),
    image: UploadFile = Depends(validate_image_page_file),
):
    return await service.create_image_page(session, chapter, index, image, mime)
