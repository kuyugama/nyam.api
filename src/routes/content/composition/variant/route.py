from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import scheme
from .scheme import CreateVolumeBody
from src.permissions import permissions
from src.database import acquire_session
from src.models import CompositionVariant
from src.util import get_offset_and_limit, paginated_response
from src.dependencies import require_page, require_permissions
from .dependencies import require_composition_variant, validate_create_volume

router = APIRouter(prefix="/variant")


@router.get(
    "/list/{slug}",
    summary="Отримати варіанти твору",
    operation_id="list_composition_variants",
    response_model=scheme.Paginated[scheme.CompositionVariant],
)
async def list_composition_variants(
    slug: str,
    page: int = Depends(require_page),
    session: AsyncSession = Depends(acquire_session),
):
    offset, limit = get_offset_and_limit(page)

    total = await service.count_variants(session, slug)
    items = await service.list_variants(session, slug, offset, limit)

    return paginated_response(items.all(), total, page, limit)


@router.get(
    "/{variant_id}",
    summary="Отримати варіант твору",
    operation_id="get_composition_variant",
    response_model=scheme.CompositionVariant,
)
async def get_composition_variant(
    variant: CompositionVariant = Depends(require_composition_variant),
):
    return variant


@router.post(
    "/{variant_id}/volume",
    summary="Створити варіант тому твору",
    operation_id="create_volume",
    response_model=scheme.Volume,
    dependencies=[
        require_permissions(permissions.volume.create, permissions.content_variant.update)
    ],
)
async def create_volume(
    body: CreateVolumeBody = Depends(validate_create_volume),
    variant: CompositionVariant = Depends(require_composition_variant),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.create_volume(session, variant, body)
