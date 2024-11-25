from .route import router

from .oauth import router as oauth_router

router.include_router(oauth_router)
