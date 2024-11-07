from fastapi import APIRouter


__all__ = ["router"]

router = APIRouter(prefix="/content", tags=["Контент"])

from .composition import router as composition_router
from .route import router as top_router

router.include_router(top_router)
router.include_router(composition_router)
