"""Generate URL slug from album name and optional slug. Uses pinyin when slug is missing."""

from pypinyin import lazy_pinyin


def slug_from_album(name: str, slug: str | None) -> str:
    """Return slug for URL: use slug if non-empty, else pinyin of name (lowercase, no spaces)."""
    if slug and slug.strip():
        return slug.strip().lower().replace(" ", "-")
    return "".join(lazy_pinyin(name)).lower()
