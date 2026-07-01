"""Slug helpers shared by WeChat migration scripts."""

from __future__ import annotations

import re

from pypinyin import lazy_pinyin


def pinyin_slug(text: str, *, max_chars: int | None = None, fallback: str = "untitled") -> str:
    """Convert text to lower-case, hyphenated pinyin slug."""
    chars: list[str] = []
    for char in text.strip():
        if char.isspace() or not char.isalnum():
            continue
        chars.append(char)
        if max_chars is not None and len(chars) >= max_chars:
            break

    source = "".join(chars)
    if not source:
        return fallback

    parts: list[str] = []
    for part in lazy_pinyin(source):
        cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", part).strip("-").lower()
        if cleaned:
            parts.append(cleaned)

    return "-".join(parts) or fallback
