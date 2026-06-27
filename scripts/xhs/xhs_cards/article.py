"""HTML renderers for Xiaohongshu article slide series."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote

from scripts.xhs.xhs_cards.article_parser import (
    load_manifest,
    merge_manifest_defaults,
    parse_article_file,
    resolve_source_path,
)
from scripts.xhs.xhs_cards.article_paginator import paginate_blocks
from scripts.xhs.xhs_cards.xhs_config import load_xhs_config

_XHS_CARDS_DIR = Path(__file__).resolve().parent
_CSS_PATH = _XHS_CARDS_DIR / "article.css"

CTA_THEME_LABELS = {
    "reading": "读书感悟",
    "life": "生活分享",
}


def _css_block() -> str:
    base = (_XHS_CARDS_DIR / "base.css").read_text(encoding="utf-8")
    article = _CSS_PATH.read_text(encoding="utf-8")
    return f"<style>{base}\n{article}</style>"


def _slide_shell(
    header: str,
    body: str,
    nickname: str,
    page: int,
    total: int,
    extra_class: str = "",
) -> str:
    slide_class = f"slide {extra_class}".strip()
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  {_css_block()}
</head>
<body>
  <div class="{slide_class}">
    <div class="slide-header">{html.escape(header)}</div>
    <div class="slide-body">{body}</div>
    <div class="slide-footer">
      <span>@{html.escape(nickname)}</span>
      <span>{page}/{total}</span>
    </div>
  </div>
</body>
</html>"""


def _render_block_html(block_kind: str, text: str) -> str:
    escaped = html.escape(text)
    if block_kind == "quote":
        return f'<div class="article-quote">{escaped}</div>'
    return f'<p class="article-p">{escaped}</p>'


def _render_body_page(header: str, blocks: list, nickname: str, page: int, total: int) -> str:
    parts = [_render_block_html(block.kind, block.text) for block in blocks]
    body = f'<div class="article-body-text">{"".join(parts)}</div>'
    return _slide_shell(header, body, nickname, page, total)


def _file_url(path: Path) -> str:
    resolved = path.resolve()
    return "file://" + quote(resolved.as_posix(), safe="/:")


def _render_cover_slide(manifest: dict[str, Any], manifest_dir: Path, page: int, total: int) -> str:
    cover_bg = manifest.get("cover_bg", "cover-bg.png")
    bg_path = manifest_dir / str(cover_bg)
    if not bg_path.is_file():
        raise FileNotFoundError(f"Cover background missing: {bg_path}")

    category_title = str(manifest.get("category_title") or "")
    xhs_title = str(manifest.get("xhs_title") or "")
    cover_subtitle = str(manifest.get("cover_subtitle") or "")
    nickname = str(manifest.get("nickname") or "")

    body = f"""
    <div class="cover-chip">{html.escape(category_title)}</div>
    <div class="cover-title">{html.escape(xhs_title)}</div>
    <div class="cover-subtitle">{html.escape(cover_subtitle)}</div>
    """
    shell = _slide_shell(category_title, body, nickname, page, total, extra_class="slide-cover")
    return shell.replace(
        '<div class="slide slide-cover">',
        f'<div class="slide slide-cover" style="background-image: url(\'{_file_url(bg_path)}\');">',
        1,
    )


def _render_end_slide(manifest: dict[str, Any], page: int, total: int) -> str:
    theme = str(manifest.get("cta_theme") or "reading")
    theme_label = CTA_THEME_LABELS.get(theme, theme)
    line1 = str(manifest.get("cta_line1") or "")
    line2 = str(manifest.get("cta_line2") or "")
    nickname = str(manifest.get("nickname") or "")
    bio = str(manifest.get("bio") or "")

    body = f"""
    <div class="end-theme">{html.escape(theme_label)}</div>
    <div class="end-line">{html.escape(line1)}</div>
    <div class="end-line">{html.escape(line2)}</div>
    <div class="end-handle">@{html.escape(nickname)}</div>
    <div class="end-bio">{html.escape(bio)}</div>
    """
    return _slide_shell(theme_label, body, nickname, page, total, extra_class="slide-end")


def render_article_slides(manifest_path: Path) -> tuple[list[tuple[str, str]], Path]:
    manifest_path = manifest_path.resolve()
    manifest_dir = manifest_path.parent
    raw_manifest = load_manifest(manifest_path)
    config = load_xhs_config()
    manifest = merge_manifest_defaults(raw_manifest, config)

    source_path = resolve_source_path(manifest, manifest_path)
    if not source_path.is_file():
        raise FileNotFoundError(f"Article source missing: {source_path}")

    article = parse_article_file(source_path)
    if not article.blocks:
        raise ValueError(f"No content blocks after parsing: {source_path}")

    max_chars = int(manifest.get("chars_per_slide", 200))
    body_pages = paginate_blocks(article.blocks, max_chars)
    total = 1 + len(body_pages) + 1

    header = str(manifest.get("category_title") or manifest.get("primary_category") or "")
    nickname = str(manifest.get("nickname") or "")

    slides: list[tuple[str, str]] = []
    slides.append(("01-cover.png", _render_cover_slide(manifest, manifest_dir, 1, total)))

    for index, blocks in enumerate(body_pages, start=2):
        filename = f"{index:02d}.png"
        html_doc = _render_body_page(header, blocks, nickname, index, total)
        slides.append((filename, html_doc))

    end_page = total
    slides.append((f"{end_page:02d}-end.png", _render_end_slide(manifest, end_page, total)))
    return slides, manifest_dir


def write_manifest(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
