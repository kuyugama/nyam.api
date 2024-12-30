from src.content_providers import get_provider
from src.scheme.error import define_error_category

define_error = define_error_category("content")
provider_not_found = define_error("provider-not-found", "Content provider not found", 404)


@provider_not_found.mark()
def require_provider(provider_name: str):
    provider_entry = get_provider(provider_name)
    if not provider_entry:
        raise provider_not_found

    return provider_entry["class_"](**provider_entry["args"])
