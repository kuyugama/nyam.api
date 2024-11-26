import re
import operator
import secrets
import unicodedata
from functools import partial
from urllib.parse import quote

import bcrypt


def camel_to_snake(name):
    return "".join(
        "_" + char.lower() if char.isupper() and i != 0 else char.lower()
        for i, char in enumerate(name)
    )


def consists_of(source: str, characters: str) -> bool:
    return all(
        map(
            partial(
                operator.contains,
                characters,
            ),
            source,
        )
    )


def secure_hash(payload: str) -> str:
    return bcrypt.hashpw(payload.encode(), bcrypt.gensalt()).decode()


def verify_payload(payload: str, payload_hash: str) -> bool:
    return bcrypt.checkpw(payload.encode(), payload_hash.encode())


# Generate URL safe slug
def slugify(
    text,
    ref: str = None,
    max_length=240,
):
    """
    Generate urlsafe slug of text.

    Code copied from https://github.com/hikka-io/hikka/blob/b373e68484d002c662bfc416adabf2a945b07c09/app/utils.py#L151-L246

    :param text: Source text
    :param ref: Reference to content
    :param max_length: Max length of slug
    :return: Resulting slug
    """
    # This used to be optional argument
    # But if we pass special characters like "?" it will break regex module
    # So it's hardcoded to "-" for the time being
    word_separator = "-"

    # https://zakon.rada.gov.ua/laws/show/55-2010-%D0%BF
    transliterate = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "h",
        "ґ": "g",
        "д": "d",
        "е": "e",
        "є": "ye",
        "ж": "zh",
        "з": "z",
        "и": "y",
        "і": "i",
        "ї": "yi",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ю": "yu",
        "я": "ya",
    }

    # Pass through text and replace cyrillic characters according to
    # official Ukrainian transliteration
    text = "".join(
        (transliterate[letter.lower()] if letter.lower() in transliterate else letter)
        for letter in text
    )

    # Remove any diacritics (accents) from the text
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

    # Convert the text to lowercase and replace spaces with the word separator
    text = re.sub(r"\s+", word_separator, text.lower())

    # Remove any non-word characters (except the word separator)
    text = re.sub(r"[^a-zA-Z0-9" + word_separator + r"]", "", text)

    # Truncate the slug if it exceeds the max_length
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip(word_separator)

    # Add content id part if specified
    if ref:
        text += word_separator + ref[:6]

    # Remove trailing word separator
    text = text.strip(word_separator)

    # Remove extra characters at the start and end
    text = text.strip("_")

    # Remove duplicate separators
    text = re.sub(word_separator + r"+", word_separator, text)

    # URL-encode the slug to handle special characters and spaces
    text = quote(text)

    # Fallback if text is empty
    if not text:
        # 22 characters (16 bytes)
        text = secrets.token_urlsafe(16)

    return text


def lower(s: str | list[str]) -> str | list[str]:
    if isinstance(s, list):
        return list(map(lower, s))

    return s.lower()
