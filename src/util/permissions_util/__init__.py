"""
+++++ PERMISSION UTILITY +++++
Created for maintaining permissions

Utility repo: https://github.com/kuyugama/permissions
"""

from typing import Sequence, Mapping

from .matching import satisfies
from .permission import Permission
from .merge import merge_permissions
from .parse import parse_permission, parse_schema
from .generate import generate_permission, generate_permissions, generate_pyi, generate_pyi_file


def check_permissions(
    required: Sequence[str | tuple[str, ...] | Permission],
    available: Mapping[str | tuple[str, ...] | Permission, bool],
) -> bool:
    for required_entry in required:
        for available_entry, allowed in available.items():
            if satisfies(available_entry, required_entry) and not allowed:
                return False

    return True
