from fastapi import APIRouter


__all__ = ["router"]

router = APIRouter(prefix="/content", tags=["Контент"])

from .composition import router as composition_router
from .chapter import router as chapter_router
from .volume import router as volume_router
from .page import router as page_router
from .route import router as top_router

router.include_router(top_router)
router.include_router(page_router)
router.include_router(volume_router)
router.include_router(chapter_router)
router.include_router(composition_router)
