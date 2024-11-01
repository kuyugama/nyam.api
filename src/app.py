import logging
from contextlib import asynccontextmanager
from typing import Callable, AsyncContextManager

import fastapi
from fastapi import APIRouter, FastAPI
from redis.asyncio import Redis
from ratelimit import setup_app
from ratelimit.store.redis import RedisStore
from ratelimit.ranking.redis import RedisRanking

import config
from src import scheme
from src.database import session_holder
from src.routes import router as main_router
from src.ratelimit import RatelimitUser, authentication_func, memory_ranking, memory_store

from src.util import (
    format_error,
    setup_route_errors,
    permission_registry,
    render_route_permissions,
)


def error_handler(_, exc: scheme.APIError):
    return exc.response


endpoint_not_found = scheme.define_error("endpoint", "not-found", "Path {path} not found", 404)


async def default_handler(scope, receive, send):
    await endpoint_not_found(extra=scope).response(scope, receive, send)


async def validation_error_handler(
    _: fastapi.Request, exc: fastapi.exceptions.RequestValidationError
):
    formatted_error = format_error(exc)

    return fastapi.responses.JSONResponse(
        formatted_error,
        status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def lifespan(test_mode: bool = True) -> Callable[[FastAPI], AsyncContextManager[None]]:
    async def lifespan(app: fastapi.FastAPI):
        if test_mode:
            ranking = memory_ranking()
            store = memory_store()
        else:
            session_holder.init(url=config.settings.postgresql.url)
            redis = Redis.from_url(url=config.settings.redis.url)
            ranking = RedisRanking(redis, RatelimitUser)
            store = RedisStore(redis)

            setup_route_errors(app)
            render_route_permissions(app)

        setup_app(
            app,
            ranking=ranking,
            store=store,
            authentication_func=authentication_func,
        )

        yield

        if not test_mode:
            await session_holder.close()

    return asynccontextmanager(lifespan)


def make_app(test_mode: bool = False) -> fastapi.FastAPI:
    logging.basicConfig(level=logging.DEBUG)
    app = fastapi.FastAPI(
        lifespan=lifespan(test_mode=test_mode),
        redoc_url=None,
        responses={422: dict(model=scheme.ValidationErrorModel)},
        openapi_tags=[
            {"name": "Авторизація"},
            {"name": "Користувачі"},
            {"name": "Ролі"},
            {"name": "default"},
        ],
    )

    router: APIRouter = getattr(app, "router")
    router.default = default_handler

    app.include_router(home_router)
    app.include_router(main_router)

    app.exception_handler(scheme.APIError)(error_handler)
    app.exception_handler(fastapi.exceptions.RequestValidationError)(validation_error_handler)

    return app


home_router = fastapi.APIRouter()


@home_router.get(
    "/",
    response_class=fastapi.responses.RedirectResponse,
    include_in_schema=False,
)
async def root():
    return fastapi.responses.RedirectResponse(
        "/docs", status_code=fastapi.status.HTTP_308_PERMANENT_REDIRECT
    )


@home_router.get("/errors")
async def errors() -> dict[str, dict[str, tuple[int, str]]]:
    return scheme.error.errors


@home_router.get("/permissions")
async def permissions() -> list[str]:
    return permission_registry
