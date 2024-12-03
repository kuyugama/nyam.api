from typing import Any
from pathlib import Path
from collections.abc import Sequence


def generate_permission(parts: Sequence[str], extra: Sequence[int]):
    """Generate permission by parts and extra"""
    body = ".".join(parts)
    if extra:
        body += "[" + ",".join(map(str, extra)) + "]"

    return body


def generate_permissions(permissions: dict | list) -> str:
    """Generate permissions by schema"""
    result = ""
    if isinstance(permissions, list):
        return "\n".join(
            permission if isinstance(permission, str) else generate_permissions(permission)
            for permission in permissions
        )

    for name, value in permissions.items():
        if not len(value):
            result += name + "\n"
            continue

        for sub in generate_permissions(value).splitlines():
            if not sub:
                continue
            result += name + "." + sub + "\n"

    return result


def simplify_permissions(permissions: dict) -> dict | list[dict | str]:
    """Generate more simple permission schema"""
    result_dict: dict[str, list[str | dict] | dict] = {}
    result_list: list[str | dict] = []

    for name, value in permissions.items():
        if not isinstance(value, dict):
            continue

        if not value:
            result_list.append(name)

        else:
            result_dict[name] = simplify_permissions(value)

    if result_list and result_dict:
        return result_list + [result_dict]

    elif result_list:
        return result_list

    return result_dict


def safe_name(name: str) -> str:
    name = name.replace("-", "_")
    if name == "*":
        name = "__"

    return name


def generate_pyi(name: str, permissions: Any, indent: int = 0) -> str:
    """Generate classes by permissions schema"""
    indent_space = " " * (4 * indent)
    inner_ident = " " * (4 * (indent + 1))
    result = f"{indent_space}class {name}(Permission):\n"

    if isinstance(permissions, dict) and indent == 0:
        permissions = simplify_permissions(permissions)

    if isinstance(permissions, list):
        for item in permissions:
            if isinstance(item, str):
                result += inner_ident + f"{safe_name(item)}: Permission\n"
            elif isinstance(item, dict):
                if not result.endswith("\n\n") and not result.endswith(":\n"):
                    result += "\n"
                for sub_key, sub_value in item.items():
                    sub_key = safe_name(sub_key)
                    result += generate_pyi(sub_key, sub_value, indent + 1)

    elif isinstance(permissions, dict):
        for key, value in permissions.items():
            key = safe_name(key)

            if isinstance(value, (list, dict)):
                if not result.endswith("\n\n") and not result.endswith(":\n"):
                    result += "\n"
                result += generate_pyi(key, value, indent + 1)

            elif isinstance(value, str):
                result += inner_ident + f"{key}: Permission\n"
    else:
        result += f"{indent_space}    pass\n"

    if not result.endswith("\n\n") and not result.endswith("pass\n"):
        result += "\n"

    return result


def generate_pyi_file(permissions: Any, output_file: str):
    """Generate .pyi file by permissions schema"""
    header = """# ==================== PERMISSIONS ====================
    # THIS IS GENERATED CODE FOR HELP IDE TO UNDERSTAND PERMISSIONS
    # ==================== PERMISSIONS ====================
    
    
    class Permission:
        parts: tuple[str, ...]
    
        def match(self, permission: str | "Permission" | tuple[str, ...]) -> bool: ...
        def satisfies(self, permission: str | "Permission" | tuple[str, ...]) -> bool: ...
        def sub(self, permission: str | tuple[str, ...]) -> "Permission": ...
        def __getitem__(self, item: str) -> "Permission": ...\n\n"""

    main_class = generate_pyi("root", permissions)
    content = "".join(
        [
            "\n".join(line.removeprefix("    ") for line in header.splitlines()),
            "\n\n",
            main_class[:-1],
            "\n\n",
            "permissions = root()",
        ]
    )

    Path(output_file).write_text(content)
