"""Shared WeChat article URL normalization and stub filename (used by migrate.py and update_manual)."""

from __future__ import annotations

import hashlib
import html

STUB_DATE = "2033-01-01"
STUB_HASH_LEN = 10


def canonical_source_url(url: str) -> str:
    u = html.unescape(url.strip())
    return u.split("#")[0]


def stub_filename_for_url(url: str) -> str:
    key = hashlib.sha256(canonical_source_url(url).encode("utf-8")).hexdigest()[:STUB_HASH_LEN]
    return f"{STUB_DATE}-post-{key}.md"
