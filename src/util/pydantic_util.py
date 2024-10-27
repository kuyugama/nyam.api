from typing import TypedDict

from fastapi.exceptions import RequestValidationError


class InvalidField(TypedDict):
    path: list[str | int] | None
    at: str
    message: str
    category: str


class ValidationError(TypedDict):
    fields: dict[str, InvalidField]
    general: str
    cat: str


def format_error(exc: RequestValidationError) -> ValidationError:
    formatted: ValidationError = {
        "fields": {},
        "general": None,
        "cat": "https://http.cat/422",
    }
    fields: dict[str, InvalidField] = formatted["fields"]

    for error in exc.errors():
        loc_len = len(error["loc"])

        name = "*" if loc_len == 1 else error["loc"][-1]

        field = fields.setdefault(name, {})

        field["path"] = error["loc"][1:] if loc_len > 2 else None
        field["at"] = error["loc"][0]

        if error["type"] in ("assertion_error", "value_error") and ", " in error["msg"]:
            error["msg"] = error["msg"].split(", ", 1)[1]

        error["msg"] = error["msg"][0].upper() + error["msg"][1:]

        field["message"] = error["msg"]
        field["category"] = error["type"]

    if len(exc.errors()) > 1:
        formatted["general"] = "There are errors in {fields} fields".format(fields=len(fields))
    else:
        field = next(iter(fields))
        field_info = fields[field]

        if field == "*":
            formatted["general"] = "Invalid {field}: {message}".format(
                field=field_info["at"],
                message=field_info["message"],
            )
        else:
            formatted["general"] = "Invalid field {field}: {message}".format(
                field=field,
                message=field_info["message"],
            )

    return formatted
