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
    simple = {
        permission: (permission if not isinstance(permission, Permission) else permission.parts)
        for permission in {**first, **second}
    }

    result: dict[str | Permission | tuple[str, ...], bool] = {}

    for first_permission, first_allowed in first.items():

        for second_permission, second_allowed in second.items():
            if satisfies(simple[second_permission], simple[first_permission]):
                if second_permission not in result:
                    result[second_permission] = second_allowed
                break
        else:
            result[first_permission] = first_allowed

    for extra_permission, allowed in second.items():
        for available in result.keys():

            if satisfies(simple[available], simple[extra_permission]):
                break
        else:
            result[extra_permission] = allowed

    print(first)
    print(second)
    print(result)

    return result
