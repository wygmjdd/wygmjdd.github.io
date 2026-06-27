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
