from fastapi import APIRouter

router = APIRouter()

from .auth import router as auth_router
from .users import router as user_router
from .roles import router as roles_router
from .content import router as content_router

router.include_router(content_router)
router.include_router(roles_router)
router.include_router(auth_router)
router.include_router(user_router)
