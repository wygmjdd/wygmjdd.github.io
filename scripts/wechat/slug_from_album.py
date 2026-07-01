"""Generate URL slug from album name."""

from scripts.wechat.slug_utils import pinyin_slug


def slug_from_album(name: str, slug: str | None) -> str:
    """Return category slug: prefer album-name pinyin, fallback to the legacy slug."""
    if name and name.strip():
        return pinyin_slug(name)
    if slug and slug.strip():
        return pinyin_slug(slug)
    return "untitled"
