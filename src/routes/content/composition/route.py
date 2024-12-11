from fastapi.params import Depends
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import scheme
from src.database import acquire_session
from ..dependencies import require_provider
from src.models import Composition, TeamMember
from .scheme import CreateCompositionVariantBody, CompositionListBody
from src.util import paginated_response, get_offset_and_limit, UseCache
from src.content_providers import SearchEntry, BaseContentProvider, ContentProviderComposition

from .dependencies import (
    require_composition,
    validate_create_variant,
    require_provider_composition,
    require_team_member,
)
from src.dependencies import (
    require_page,
    require_use_cache,
    require_drop_cache,
)

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
    dependencies=[require_drop_cache("composition")],
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
async def get_composition(composition: Composition = Depends(require_composition)):
    return composition


@router.post(
    "/list",
    summary="Отримати список творів",
    response_model=scheme.Paginated[scheme.Composition],
    operation_id="list_composition",
)
async def list_compositions(
    body: CompositionListBody,
    session: AsyncSession = Depends(acquire_session),
    use_cache: UseCache = require_use_cache("composition"),
    page: int = Depends(require_page),
):
    offset, limit = get_offset_and_limit(page)

    total = await use_cache(body.cache_key(), service.count_compositions(session, body))
    items = await service.list_compositions(session, body, offset, limit)

    return paginated_response(items.all(), total, page, limit)


@router.post(
    "/{slug}/variant",
    summary="Опублікувати варіант твору",
    response_model=scheme.CompositionVariant,
    operation_id="create_composition_variant",
)
async def publish_composition_variant(
    body: CreateCompositionVariantBody = Depends(validate_create_variant),
    team_member: TeamMember = Depends(require_team_member),
    origin: Composition = Depends(require_composition),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.publish_composition_variant(session, origin, body, team_member)
