from fastapi import APIRouter

from src import scheme
from src.content_providers import provider_registry

router = APIRouter()


@router.get(
    "/providers",
    summary="Отримати всі підтримувані провайдери контенту",
    response_model=list[scheme.ContentProvider],
    operation_id="get_content_providers",
)
async def get_providers():
    return provider_registry.values()
