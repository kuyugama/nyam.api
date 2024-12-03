def parse_permission(permission: str) -> dict[str, list[str | int]]:
    """Parse one permission to parts and extra"""
    extra = []
    parts = []

    extra_opened = 0b1

    part = ""
    flags = 0
    for char in permission:
        if char == "[" and flags & extra_opened:
            raise ValueError("Extra in extra")

        if flags & extra_opened:
            match char:
                case "]":
                    extra.append(int(part))
                    part = ""
                    flags ^= extra_opened

                case ",":
                    extra.append(int(part))
                    part = ""
                case _:
                    part += char

            continue

        match char:
            case ".":
                if part:
                    parts.append(part)
                part = ""
                continue

            case "[":
                flags ^= extra_opened
                parts.append(part)
                part = ""
            case _:
                part += char

    if flags & extra_opened and part:
        extra.append(int(part))
        part = ""

    if part:
        parts.append(part)

    return {"parts": parts, "extra": extra}


def parse_schema(permissions: str) -> dict:
    """Parse permissions schema"""
    result: dict[str, dict] = {}

    for line in permissions.split("\n"):
        parts = parse_permission(line.strip())["parts"]
        root = result
        for part in parts:
            root = root.setdefault(part, {})

    return result
