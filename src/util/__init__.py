import math
import typing

from sqlalchemy.orm import DeclarativeBase

from src import constants

from .string_util import lower
from .datetime_util import now
from .s3_util import delete_obj
from .string_util import slugify
from .image_util import file_size
from .image_util import compress_png
from .string_util import secure_hash
from .string_util import consists_of
from .s3_util import upload_file_obj
from .fastapi_util import has_errors
from .hash_util import cache_key_hash
from .string_util import verify_payload
from .string_util import camel_to_snake
from .pydantic_util import format_error
from .datetime_util import utc_timestamp
from .sqlalchemy_util import update_by_pk
from .image_util import filter_image_size
from .fastapi_util import setup_route_errors
from .fastapi_util import route_has_dependency
from .permissions_util import check_permissions
from .permissions_util import permission_registry
from .fastapi_util import render_route_permissions
from .sqlalchemy_util import update_within_flush_event


__all__ = [
    "now",
    "lower",
    "slugify",
    "UseCache",
    "file_size",
    "has_errors",
    "delete_obj",
    "secure_hash",
    "compress_png",
    "consists_of",
    "update_by_pk",
    "format_error",
    "utc_timestamp",
    "cache_key_hash",
    "camel_to_snake",
    "verify_payload",
    "upload_file_obj",
    "PermissionChecker",
    "filter_image_size",
    "check_permissions",
    "setup_route_errors",
    "paginated_response",
    "permission_registry",
    "route_has_dependency",
    "get_offset_and_limit",
    "render_route_permissions",
    "update_within_flush_event",
]


def get_offset_and_limit(page: int, size: int = constants.DEFAULT_PAGE_SIZE):
    return (page - 1) * size, size


def paginated_response(
    items: typing.Sequence[DeclarativeBase],
    total: int,
    page: int,
    limit: int,
):
    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "pages": math.ceil(total / limit),
        },
    }


T = typing.TypeVar("T")


class UseCache(typing.Protocol):
    @staticmethod
    async def __call__(cache_key: tuple[typing.Any, ...], coro: typing.Awaitable[T]) -> T: ...


class PermissionChecker(typing.Protocol):
    @staticmethod
    def __call__(*permissions: str): ...
