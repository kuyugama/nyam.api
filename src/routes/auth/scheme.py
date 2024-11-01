from string import ascii_letters, digits

from pydantic import EmailStr, field_validator

from src.util import consists_of
from src.scheme.model import SchemeModel


class SignUpBody(SchemeModel):
    email: EmailStr
    nickname: str
    password: str

    @field_validator("nickname")
    def validate_nickname(cls, v: str):
        assert len(v) > 5, "Nickname length cannot be less than 5 characters"

        assert consists_of(
            v, ascii_letters + digits + "_"
        ), "Nickname can contain only ascii-letters, numbers and underscores"

        return v


class SignInEmailBody(SchemeModel):
    email: EmailStr
    password: str


class SignInNicknameBody(SchemeModel):
    nickname: str
    password: str


SignInBody = SignInEmailBody | SignInNicknameBody
