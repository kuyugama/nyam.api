from fastapi.params import Depends
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from src import scheme, permissions
from src.models import Composition, Token
from src.database import acquire_session
from ..dependencies import require_provider
from .scheme import CreateCompositionVariantBody
from src.dependencies import require_token, require_permissions
from src.content_providers import SearchEntry, BaseContentProvider, ContentProviderComposition

from .dependencies import (
    require_composition,
    validate_publish_variant,
    require_provider_composition,
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
    "/{slug}/variant",
    summary="Опублікувати варіант твору",
    description="""Увага! Прихована перевірка дозволів. 
Вам необхідно мати право "content.{{composition.style}}.update" 
для публікації варіанту твору""",
    response_model=scheme.CompositionVariant,
    operation_id="create_composition_variant",
    dependencies=[require_permissions(permissions.content_variant.create)],
)
async def publish_composition_variant(
    body: CreateCompositionVariantBody = Depends(validate_publish_variant),
    author_token: Token = Depends(require_token),
    origin: Composition = Depends(require_composition),
    session: AsyncSession = Depends(acquire_session),
):
    return await service.publish_composition_variant(session, origin, body, author_token.owner)
