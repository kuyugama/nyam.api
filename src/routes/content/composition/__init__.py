from .route import router

from .variant import router as variant_router

router.include_router(variant_router)

__all__ = ["router"]
