from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import scheme, constants
from src.database import acquire_session
from src.models import Chapter, TextPage, ImagePage
from src.dependencies import require_chapter, require_page, require_content_page
from src.util import get_offset_and_limit, paginated_response
from src.service import get_composition_variant_by_chapter_id

router = APIRouter(prefix="/page")


IMAGE_TYPE_TO_MODEL = {
    constants.PAGE_TEXT: TextPage,
    constants.PAGE_IMAGE: ImagePage,
}


@router.get(
    "/list/{chapter_id}",
    summary="Отримати сторінки розділу",
    operation_id="list_pages",
    response_model=scheme.Paginated[scheme.ImagePage] | scheme.Paginated[scheme.TextPage],
)
async def list_pages(
    page: int = Depends(require_page),
    chapter: Chapter = Depends(require_chapter),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    variant = await get_composition_variant_by_chapter_id(session, chapter.id)

    model = IMAGE_TYPE_TO_MODEL[constants.COMPOSITION_STYLE_TO_PAGE_TYPE[variant.origin.style]]

    items = await service.list_pages(session, chapter.id, offset, limit, model)

    return paginated_response(items.all(), chapter.pages, page, limit)


@router.get(
    "/{page_id}",
    summary="Отримати сторінку",
    operation_id="get_page",
    response_model=scheme.TextPage | scheme.ImagePage,
)
async def get_page(page: ImagePage | TextPage = Depends(require_content_page)):
    return page
