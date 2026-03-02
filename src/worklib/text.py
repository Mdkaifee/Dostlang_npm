"""Text utility functions exposed by the library."""

import re


def slugify(value: str) -> str:
    """Convert text to a lowercase hyphen-separated slug."""
    cleaned = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE).strip().lower()
    return re.sub(r"[-\s]+", "-", cleaned)


def title_case(value: str) -> str:
    """Return text in title case with single-spaced words."""
    squashed = " ".join(value.split())
    return squashed.title()
