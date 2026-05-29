from __future__ import annotations

from app.config import settings
from app.middleware.error_handler import BadRequestException


def normalize_page_size(page_size: int) -> int:
    if page_size < 1:
        raise BadRequestException("page_size must be >= 1")
    return min(page_size, settings.API_MAX_PAGE_SIZE)


def normalize_search(search: str | None) -> str | None:
    if search is None:
        return None
    value = search.strip()
    if len(value) > settings.API_MAX_SEARCH_LENGTH:
        raise BadRequestException(
            f"search must be {settings.API_MAX_SEARCH_LENGTH} characters or fewer"
        )
    return value or None

