from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import scheme, permissions
from src.database import acquire_session
from src.models import CompositionVariant, Volume
from src.util import get_offset_and_limit, paginated_response
from src.dependencies import (
    require_composition_variant,
    require_page,
    require_volume,
    require_permissions,
)
from .dependencies import validate_create_chapter
from .scheme import CreateChapterBody

router = APIRouter(prefix="/volume")


@router.get(
    "/list/{variant_id}",
    summary="Отримати томи варіанту твору",
    operation_id="list_volumes",
    response_model=scheme.Paginated[scheme.Volume],
)
async def list_volumes(
    page: int = Depends(require_page),
    variant: CompositionVariant = Depends(require_composition_variant),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    items = await service.list_volumes(session, variant.id, offset, limit)

    return paginated_response(items.all(), variant.volumes, page, limit)


@router.get(
    "/{volume_id}",
    summary="Отримати том варіанту твору",
    operation_id="get_volume",
    response_model=scheme.Volume,
)
async def get_volume(volume: Volume = Depends(require_volume)):
    return volume


@router.post(
    "/{volume_id}/chapter",
    summary="Створити розділ тому",
    operation_id="create_chapter",
    response_model=scheme.Chapter,
    dependencies=[require_permissions(permissions.chapter.create)],
)
async def create_chapter(
    body: CreateChapterBody = Depends(validate_create_chapter),
    volume: Volume = Depends(require_volume),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.create_chapter(session, volume, body)
