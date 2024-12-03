from typing import overload, Mapping

from . import Permission
from .matching import satisfies


@overload
def merge_permissions(
    first: Mapping[Permission, bool], second: Mapping[Permission, bool]
) -> dict[Permission, bool]: ...


@overload
def merge_permissions(first: Mapping[str, bool], second: Mapping[str, bool]) -> dict[str, bool]: ...


@overload
def merge_permissions(
    first: Mapping[tuple[str, ...], bool], second: Mapping[tuple[str, ...], bool]
) -> dict[tuple[str, ...], bool]: ...


def merge_permissions(
    first: Mapping[str | Permission | tuple[str, ...], bool],
    second: Mapping[str | Permission | tuple[str, ...], bool],
) -> dict[str | Permission | tuple[str, ...], bool]:
    """
    Merge second permission mapping into first
    """
    result: dict[Permission, bool] = {}

    for first_permission, first_allowed in first.items():
        left = first_permission
        if isinstance(first_permission, Permission):
            left = first_permission.parts

        for second_permission, second_allowed in second.items():

            right = second_permission
            if isinstance(second_permission, Permission):
                right = second_permission.parts

            if satisfies(right, left):
                if second_permission not in result:
                    result[second_permission] = second_allowed
                break
        else:
            result[first_permission] = first_allowed

    return result
