from typing import Union
from functools import lru_cache

from .generate import generate_permission
from .matching import matches, satisfies


def _get_sub_schema(schema: dict | list, name: str) -> dict | list | None:
    if isinstance(schema, dict) and name in schema:
        return schema[name]

    for element in schema:
        if element == name:
            return {}

        if isinstance(element, dict) and name in element:
            return element[name]


class Permission:
    def __init__(self, schema: dict | list, parts: tuple[str, ...] = (), extra: list[int] = None):
        self.schema = schema
        self.parts = parts or ""
        self.parts_max_index = len(self.parts) - 1
        self.extra = extra or []

    @lru_cache
    def _exist_in_schema(self, parts: tuple[str, ...]) -> bool:
        schema = self.schema
        for part in parts:
            schema = _get_sub_schema(schema, part)

            if schema is None:
                return False

        return True

    def sub(self, permission: str | tuple[str, ...]) -> "Permission":
        if isinstance(permission, tuple):
            parts = permission
        else:
            parts = (permission,)

        if self.parts:
            parts = self.parts + parts

        if self._exist_in_schema(parts):
            return Permission(self.schema, parts)

    @property
    def name(self):
        return generate_permission(self.parts, self.extra)

    def match(self, permission: Union[str, tuple[str, ...], "Permission"]) -> bool:
        """
        Check if this permission matches the given permission.

        :param permission: Permission to match.
        :return: Check result.
        """
        if isinstance(permission, Permission):
            permission = permission.parts

        return matches(self.parts, permission)

    def satisfies(self, permission: Union[str, tuple[str, ...], "Permission"]) -> bool:
        """
        Check if this permission satisfies the given permission.

        :param permission: Permission to check.
        :return: Check result.
        """
        if isinstance(permission, Permission):
            permission = permission.parts

        return satisfies(self.parts, permission)

    def __eq__(self, other):
        return self.match(other)

    def __hash__(self):
        return hash(self.parts)

    def __getattr__(self, name: str):
        if name in ("_", "__"):
            name = "*"

        return self.sub(name.replace("_", "-"))

    def __getitem__(self, name: str):
        return self.sub(name)

    def __repr__(self):
        return "Permission({})".format(self.name)

    def __str__(self):
        return self.name
