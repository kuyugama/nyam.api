from fastapi import APIRouter

import config
from src.scheme import define_error, Bot

bot_not_found = define_error("bot", "not-found", "Bot not found", 404)

router = APIRouter()


@router.get("/bot/{code}", responses={404: dict(model=bot_not_found.model)}, response_model=Bot)
async def get_bot(code: str):
    if not code in config.settings.bot:
        raise bot_not_found

    return config.settings.bot[code]


from .auth import router as auth_router
from .users import router as user_router
from .roles import router as roles_router
from .content import router as content_router

router.include_router(content_router)
router.include_router(roles_router)
router.include_router(auth_router)
router.include_router(user_router)
