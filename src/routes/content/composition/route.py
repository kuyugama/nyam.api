from fastapi import APIRouter, Query
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import scheme
from src.database import acquire_session
from . import service
from .dependencies import require_provider_composition
from ..dependencies import require_provider
from src.content_providers import SearchEntry, BaseContentProvider, ContentProviderComposition

router = APIRouter(prefix="/composition")


@router.get(
    "/{provider_name}/search",
    summary="Здійснити пошук за допомогою провайдера контенту",
    response_model=scheme.Paginated[SearchEntry],
    operation_id="provider_search_composition",
)
async def get_search_provider(
    query: str,
    provider: BaseContentProvider = Depends(require_provider),
    page: int = Query(1, ge=1),
):
    return await provider.search_composition(query, page)


@router.put(
    "/{provider_name}/{provider_id}",
    summary="Опублікувати твір використовуючи інформацію з провайдера контенту",
    response_model=scheme.Composition,
    operation_id="publish_composition_from_provider",
)
async def publish_composition_from_provider(
    provider_composition: ContentProviderComposition = Depends(require_provider_composition),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.publish_composition_from_provider(session, provider_composition)


@router.get(
    "/{slug}",
    summary="Отримати твір",
    response_model=scheme.Composition,
    operation_id="get_composition",
)
async def get_composition(slug: str, session: AsyncSession = Depends(acquire_session)):
    return await service.get_composition_by_slug(session, slug)
