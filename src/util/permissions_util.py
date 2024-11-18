import inspect

from .string_util import camel_to_snake
from collections.abc import Sequence
from typing import Union, Mapping

permission_registry = ["*"]


def gather_permissions(root: type["Permission"], prefix: str = "") -> list[str]:
    annotations = inspect.get_annotations(root)
    permissions = [prefix + "*"]

    for name, type_ in annotations.items():
        name = name.replace("_", "-")
        if issubclass(type_, Permission):
            permissions.extend(gather_permissions(type_, prefix + name + "."))
        else:
            permissions.append(prefix + name)

    return permissions


class Permission(str):
    """
    Permission utility class.

    Example:
    ::
        class UserOwn(Permission):
            update_info: str


        class User(Permission):
            own: UserOwn
            update_info: str

        user = User()
        print(user.update_info)
        print(user.own.update_info)
        print(user.own.update_info | user.update_info nm)
    """

    def __init__(self, permission: str | None = None):
        self.permission = permission or camel_to_snake(type(self).__qualname__).replace("_", "-")
        self.space = type(self).__annotations__

        if permission is None:
            permission_registry.extend(
                sorted(gather_permissions(type(self), self.permission + "."))
            )

    def use_space(self, space: type):
        self.space = {} if space is str else space.__annotations__
        return self

    def __str__(self):
        return self.permission

    def __or__(self, other: Union["Permission", str]):
        return "{self} | {other}".format(self=self, other=other)

    def __ror__(self, other):
        return "{other} | {self}".format(self=self, other=other)

    def sub(self, permission: str):
        if permission not in self.space:
            raise AttributeError(f"Permission not defined: {self.permission} -> {permission}")

        return Permission(self.permission + "." + permission.replace("_", "-")).use_space(
            self.space[permission]
        )

    def __getattr__(self, attr):
        return self.sub(attr)

    def __getitem__(self, item):
        return self.sub(item)


def match(required: str, available: str) -> bool:
    """
    Match a pair of permissions

    Examples:
    ::
        match("user.own.update-email", "")  # ----------------------- False
        match("user.own.update-email", "*")  # ---------------------- True
        match("user.own.update-email", "user.*")  # ----------------- True
        match("user.own.update-email", "user.own.*")  # ------------- True
        match("user.own.update-email", "user.own.update-email")  # -- True
        match("user.own.update-email", "user.own.update-nickname")  # False
    """
    if available == "":
        return False

    if "|" in required:
        return any(
            map(
                lambda r: match(r.strip(), available),
                required.split("|"),
            )
        )

    required_parts = required.split(".")
    available_parts = available.split(".")

    if len(available_parts) != len(required_parts) and "*" not in available_parts:
        return False

    for index, part in enumerate(available_parts):
        if part == "*":
            return True

        if part != required_parts[index]:
            return False

    return True


def permission_present(required: str, available: Mapping[str, bool]) -> bool:
    """Check if required permission is True in ``available`` permissions"""

    # Don't run for-loop if "grant-all" ("*") is present
    if "*" in available:
        # If "*" is false - user don't have right to do anything
        return available["*"]

    for name, allowed in available.items():
        if match(required, name):
            return allowed

    return False


def check_permissions(required: Sequence[str], available: Mapping[str, bool]) -> bool:
    """
    Check for permissions.

    Checks for permissions in format ``category.subcategory.name``

    Allows "*" to be present in ``available`` permission parts - acts as "grant-all"
    """

    # Don't run for-loop if "grant-all" ("*") is present
    if "*" in available:
        # If "*" is false - user don't have right to do anything
        return available["*"]

    for entry in required:
        if not permission_present(entry, available):
            return False

    return True
