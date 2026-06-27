"""Load Xiaohongshu card config and Hugo category titles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_XHS_CARDS_DIR = Path(__file__).resolve().parent
_XHS_DIR = _XHS_CARDS_DIR.parent
REPO_ROOT = _XHS_DIR.parent.parent
CONFIG_PATH = _XHS_DIR / "config.yml"
CATEGORIES_PATH = REPO_ROOT / "data" / "categories.yml"
SUPPORTED_MANIFEST_VERSION = 1


def load_xhs_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"Missing config: {CONFIG_PATH}")
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid config format: {CONFIG_PATH}")
    return data


def load_category_titles() -> dict[str, str]:
    if not CATEGORIES_PATH.is_file():
        return {}
    raw = yaml.safe_load(CATEGORIES_PATH.read_text(encoding="utf-8"))
    titles: dict[str, str] = {}
    if isinstance(raw, list):
        for row in raw:
            if isinstance(row, dict) and row.get("slug"):
                titles[str(row["slug"]).strip()] = str(row.get("title") or row["slug"]).strip()
    return titles


def resolve_category_title(slug: str) -> str:
    return load_category_titles().get(slug, slug)


def resolve_cta_theme(primary_category: str, config: dict[str, Any] | None = None) -> str:
    cfg = config or load_xhs_config()
    mapping = cfg.get("cta_mapping") or {}
    for theme, slugs in mapping.items():
        if isinstance(slugs, list) and primary_category in slugs:
            return str(theme)
    default = cfg.get("default_cta", "reading")
    return str(default)


def enrich_manifest_from_article(manifest: dict[str, Any], article_metadata: dict[str, Any]) -> dict[str, Any]:
    """Fill primary_category and category_title from Hugo front matter when manifest omits them."""
    merged = dict(manifest)
    if not str(merged.get("primary_category") or "").strip():
        slug_raw = article_metadata.get("primary_category")
        if slug_raw is not None and str(slug_raw).strip():
            merged["primary_category"] = str(slug_raw).strip()

    slug = str(merged.get("primary_category") or "").strip()
    if slug and not str(merged.get("category_title") or "").strip():
        merged["category_title"] = resolve_category_title(slug)
    return merged
