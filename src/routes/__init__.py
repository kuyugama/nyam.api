from fastapi import APIRouter

router = APIRouter()

from .users import router as user_router
from .auth import router as auth_router
from .roles import router as roles_router

router.include_router(roles_router)
router.include_router(auth_router)
router.include_router(user_router)
