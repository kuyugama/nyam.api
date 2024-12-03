from .parse import parse_permission


def satisfies(left: str | tuple[str, ...], right: str | tuple[str, ...]) -> bool:
    """
    Check if the left permission satisfies the right permission.

    :param left: The left permission.
    :param right: The right permission.
    :return: True if the permission satisfies the right permission, False otherwise.
    """
    if isinstance(left, str):
        left_parts = parse_permission(left)["parts"]
    else:
        left_parts = left

    if isinstance(right, str):
        right_parts = parse_permission(right)["parts"]
    else:
        right_parts = right

    right_max_index = len(right_parts) - 1

    if left_parts == right_parts:
        return True

    for i, part in enumerate(left_parts):
        if i > right_max_index:
            break

        if right_parts[i] != part and not part == "*":
            return False

    return True


def matches(left: str | tuple[str, ...], right: str | tuple[str, ...]) -> bool:
    """
    Check if the left permission matches the right permission.

    :param left: The left permission.
    :param right: The right permission.
    :return: True if the permission matches the right permission, False otherwise.
    """

    return satisfies(left, right) or satisfies(right, left)
