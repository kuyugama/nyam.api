import functools
from types import FunctionType
from typing import cast, Protocol, Callable

import fastapi
from pydantic import Field
from pydantic import HttpUrl

from .model import SchemeModel
from src.util import snake_to_camel


class InvalidField(SchemeModel):
    path: list[str | int] | None = Field(description="Path to deep fields")
    at: str = Field(description="Field location: path, query, body, header")
    message: str = Field(description="The message of the error")
    category: str = Field(description="The category of the error")


class ValidationErrorModel(SchemeModel):
    fields: dict[str, InvalidField] = Field(
        description="Dictionary of fields that failed validation",
        examples=[
            {
                "nickname": InvalidField(
                    path=None,
                    at="body",
                    message="Nickname can contain only ascii-letters, numbers and underscores",
                    category="assertion_error",
                )
            },
        ],
    )
    general: str = Field(
        description="General error message",
        examples=[
            "Invalid field nickname: Nickname can contain only ascii-letters, numbers and underscores"
        ],
    )
    cat: HttpUrl = Field(description="Error cat", examples=["https://http.cat/422"])


class ErrorModel(SchemeModel):
    message: str = Field(description="Error message", examples=["User not found"])
    category: str = Field(description="Error category", examples=["users"])
    code: str = Field(description="Error code", examples=["not-found"])
    cat: HttpUrl = Field(description="Error cat", examples=["https://http.cat/404"])


# All errors are generated at runtime, to get all available errors - make request to GET /errors
# {"CATEGORY": {"CODE": (STATUS_CODE, "MESSAGE")}}
errors = {
    "auth": {
        "password-occupied": (400, "Password occupied"),  # Hehe :3
    }
}


class APIError(fastapi.HTTPException):
    models: dict[str, type[ErrorModel]] = {}

    def __class_getitem__(cls, item: tuple[str, str]) -> type[ErrorModel]:
        """
        Generate error model for specific category and code.
        This used only for endpoint response schema generation
        """
        category, code = item
        if errors.get(category) is None or errors.get(category, {}).get(code) is None:
            raise ValueError(f"Invalid error {category} => {code}")

        model_name = (
            "Error_"
            + snake_to_camel(category, "/")
            + "_"
            + "".join(word.capitalize() for word in code.split("-"))
        )

        if model_name in cls.models:
            return cls.models[model_name]

        origin_fields = ErrorModel.model_fields

        message_description = origin_fields["message"].description
        category_description = origin_fields["category"].description
        code_description = origin_fields["code"].description
        cat_description = origin_fields["cat"].description

        status, message = errors[category][code]

        model = cast(
            type[ErrorModel],
            type(
                model_name,
                (SchemeModel,),
                {
                    "__annotations__": {
                        "code": str,
                        "category": str,
                        "message": str,
                        "cat": HttpUrl,
                    },
                    "code": Field(code, description=code_description),
                    "category": Field(category, description=category_description),
                    "message": Field(message, description=message_description),
                    "cat": Field(
                        "https://http.cat/{cat}".format(cat=status),
                        description=cat_description,
                    ),
                },
            ),
        )

        cls.models[model_name] = model

        return model

    def __init__(
        self,
        category: str,
        code: str,
        headers: dict[str, str] | None = None,
        extra: dict[str, str] | None = None,
    ):
        self.code = code
        self.extra = extra
        self.headers = headers
        self.category = category
        self.status_code, self.message = errors[category][code]

        self.formatted_message = self.message
        if self.extra is not None:
            self.formatted_message = self.message.format(**extra)

    def __repr__(self):
        return f"APIError<{self.category}:{self.code}:{self.status_code}>({self.message!r})"

    def __str__(self):
        return f"{self.category}+{self.code}: {self.formatted_message}"

    def __call__(self, extra: dict[str, str] | None = None, headers: dict[str, str] | None = None):
        return APIError(self.category, self.code, headers or self.headers, extra)

    @property
    def response(self) -> fastapi.responses.JSONResponse:
        return fastapi.responses.JSONResponse(
            content=ErrorModel(
                message=self.formatted_message,
                category=self.category,
                code=self.code,
                cat="https://http.cat/{cat}".format(cat=self.status_code),
            ).model_dump(mode="json"),
            status_code=self.status_code,
            headers=self.headers,
        )

    @property
    def model(self) -> type[ErrorModel]:
        return cast(type[ErrorModel], APIError[self.category, self.code])

    def mark(self, func: FunctionType | Callable = None):
        """Mark function as dependency that raises this error"""

        # If used as:
        # @error.mark()
        # def func(): ...
        if func is None:
            return self.mark

        from src.util import has_errors

        has_errors(self)(func)

        return func


def define_error(category: str, code: str, message: str, status: int) -> APIError:
    category_dict = errors.setdefault(category, {})
    category_dict.setdefault(code, (status, message))

    return APIError(category, code)


class _DefineError(Protocol):
    @staticmethod
    def __call__(code: str, message: str, status: int) -> APIError: ...


def define_error_category(category: str) -> _DefineError:
    return functools.partial(define_error, category)
