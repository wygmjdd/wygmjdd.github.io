"""HTML renderers for Xiaohongshu article slide series."""

from __future__ import annotations

import base64
import html
import shutil
import sys
from pathlib import Path
from typing import Any

from scripts.xhs.xhs_cards.article_parser import (
    ContentBlock,
    load_manifest,
    merge_manifest_defaults,
    parse_article_file,
    resolve_source_path,
)
from scripts.xhs.xhs_cards.article_browser_paginator import paginate_blocks_with_browser
from scripts.xhs.xhs_cards.article_paginator import _merge_adjacent_blocks
from scripts.xhs.xhs_cards.xhs_config import enrich_manifest_from_article, load_xhs_config

_XHS_CARDS_DIR = Path(__file__).resolve().parent
_CSS_PATH = _XHS_CARDS_DIR / "article.css"
_BODY_SLIDE_WARN_THRESHOLD = 12

COVER_AI_FILENAME = "cover-ai.png"
COVER_BG_FILENAME = "cover-bg.png"
COVER_OUTPUT_FILENAME = "01-cover.png"

CTA_THEME_LABELS = {
    "reading": "读书感悟",
    "life": "生活分享",
}

_CSS_BLOCK_CACHE: str | None = None


def _css_block() -> str:
    global _CSS_BLOCK_CACHE
    if _CSS_BLOCK_CACHE is None:
        base = (_XHS_CARDS_DIR / "base.css").read_text(encoding="utf-8")
        article = _CSS_PATH.read_text(encoding="utf-8")
        _CSS_BLOCK_CACHE = f"<style>{base}\n{article}</style>"
    return _CSS_BLOCK_CACHE


def clear_css_cache() -> None:
    """Drop cached inline CSS (tests / dev rerenders)."""
    global _CSS_BLOCK_CACHE
    _CSS_BLOCK_CACHE = None


def _slide_shell(
    body: str,
    extra_class: str = "",
    background_url: str | None = None,
    *,
    nickname: str = "",
    page: int = 0,
    total: int = 0,
    show_page_footer: bool = False,
) -> str:
    slide_class = f"slide {extra_class}".strip()
    style_attr = ""
    if background_url:
        style_attr = f' style="background-image: url(\'{background_url}\');"'
    footer_html = ""
    if show_page_footer:
        footer_html = f"""
    <div class="slide-footer">
      <span>@{html.escape(nickname)}</span>
      <span class="footer-page">{page}/{total}</span>
    </div>"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  {_css_block()}
</head>
<body>
  <div class="{slide_class}"{style_attr}>
    <div class="slide-body">{body}</div>{footer_html}
  </div>
</body>
</html>"""


def _render_block_html(block_kind: str, text: str, *, paragraph_start: bool = True) -> str:
    escaped = html.escape(text)
    if block_kind == "quote":
        return f'<div class="article-quote">{escaped}</div>'
    paragraph_class = "article-p article-p-start" if paragraph_start else "article-p article-p-continue"
    return f'<p class="{paragraph_class}">{escaped}</p>'


def _collapse_paragraph_blocks(blocks: list) -> list:
    """Merge consecutive paragraph blocks from the same source for seamless rendering."""
    collapsed: list = []
    for block in blocks:
        if (
            collapsed
            and block.kind == "paragraph"
            and collapsed[-1].kind == "paragraph"
            and collapsed[-1].source_id == block.source_id
        ):
            previous = collapsed[-1]
            collapsed[-1] = ContentBlock(
                previous.kind,
                previous.text + block.text,
                previous.source_id,
            )
            continue
        collapsed.append(block)
    return collapsed


def _render_body_page(
    header: str,
    blocks: list,
    page: int,
    total: int,
    nickname: str,
    *,
    continues_paragraph: bool = False,
) -> str:
    parts: list[str] = []
    seen_sources: set[int] = set()
    for index, block in enumerate(_collapse_paragraph_blocks(blocks)):
        if block.kind == "quote":
            parts.append(_render_block_html(block.kind, block.text))
            continue

        paragraph_start = True
        if block.source_id in seen_sources:
            paragraph_start = False
        elif index == 0 and continues_paragraph:
            paragraph_start = False
        seen_sources.add(block.source_id)
        parts.append(_render_block_html(block.kind, block.text, paragraph_start=paragraph_start))

    body = f"""
    <div class="frame-header">{html.escape(header)}</div>
    <div class="article-body-text">{"".join(parts)}</div>
    """
    return _slide_shell(
        body,
        extra_class="slide-article",
        nickname=nickname,
        page=page,
        total=total,
        show_page_footer=True,
    )


def _image_data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def prepare_cover_ai(manifest_dir: Path, manifest: dict[str, Any]) -> Path | None:
    """Return optional cover background path, copying legacy cover-bg when present."""
    ai_path = manifest_dir / COVER_AI_FILENAME
    if ai_path.is_file():
        return ai_path

    declared_background = False
    for key in ("cover_ai", "cover_bg"):
        name = manifest.get(key)
        if not isinstance(name, str) or not name.strip():
            continue
        declared_background = True
        legacy = manifest_dir / name.strip()
        if legacy.is_file() and legacy.resolve() != ai_path.resolve():
            shutil.copy2(legacy, ai_path)
            return ai_path
        if legacy.is_file():
            return legacy

    fallback = manifest_dir / COVER_BG_FILENAME
    if fallback.is_file():
        shutil.copy2(fallback, ai_path)
        return ai_path

    if declared_background:
        raise FileNotFoundError(
            f"Declared cover background missing. Expected {ai_path} or the manifest cover path in {manifest_dir}"
        )

    return None


def sync_cover_deliverables(manifest_dir: Path) -> None:
    """After render, 01-cover.png and cover-bg.png are the same final cover."""
    cover_out = manifest_dir / COVER_OUTPUT_FILENAME
    if not cover_out.is_file():
        return
    shutil.copy2(cover_out, manifest_dir / COVER_BG_FILENAME)


def _render_cover_slide(manifest: dict[str, Any], manifest_dir: Path) -> str:
    ai_path = prepare_cover_ai(manifest_dir, manifest)
    xhs_title = str(manifest.get("xhs_title") or "")
    theme = str(manifest.get("cta_theme") or "reading")
    theme_label = CTA_THEME_LABELS.get(theme, theme)

    body = f"""
    <div class="cover-title-card glass-card">
      <div class="cover-kicker">{html.escape(theme_label)}</div>
      <div class="cover-title">{html.escape(xhs_title)}</div>
    </div>
    """
    return _slide_shell(
        body,
        extra_class="slide-cover",
        background_url=_image_data_url(ai_path) if ai_path else None,
    )


def _render_end_slide(manifest: dict[str, Any]) -> str:
    theme = str(manifest.get("cta_theme") or "reading")
    theme_label = CTA_THEME_LABELS.get(theme, theme)
    line1 = str(manifest.get("cta_line1") or "")
    nickname = str(manifest.get("nickname") or "")
    bio = str(manifest.get("bio") or "")

    body = f"""
    <div class="end-theme">{html.escape(theme_label)}</div>
    <div class="end-line">{html.escape(line1)}</div>
    <div class="end-handle">@{html.escape(nickname)}</div>
    <div class="end-bio">{html.escape(bio)}</div>
    """
    return _slide_shell(body, extra_class="slide-end")


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
    manifest = enrich_manifest_from_article(manifest, article.metadata)
    if not article.blocks:
        raise ValueError(f"No content blocks after parsing: {source_path}")

    max_chars = int(manifest.get("chars_per_slide", 340))

    header = str(manifest.get("xhs_title") or manifest.get("series_title") or "")
    nickname = str(manifest.get("nickname") or "")

    def _page_continues_from_previous(all_pages: list, page_index: int, blocks: list) -> bool:
        if page_index <= 0 or not all_pages[page_index - 1] or not blocks:
            return False
        previous_last = all_pages[page_index - 1][-1]
        first_block = blocks[0]
        return (
            previous_last.kind == "paragraph"
            and first_block.kind == "paragraph"
            and previous_last.source_id == first_block.source_id
        )

    def _render_probe_page(blocks: list, probe_total: int, page_index: int = 0, all_pages: list | None = None) -> str:
        pages_snapshot = all_pages if all_pages is not None else body_pages
        continues = _page_continues_from_previous(pages_snapshot, page_index, blocks)
        return _render_body_page(
            header,
            blocks,
            1,
            max(probe_total, 1),
            nickname,
            continues_paragraph=continues,
        )

    body_pages = paginate_blocks_with_browser(
        article.blocks,
        _render_probe_page,
        max_chars=max_chars,
    )
    body_pages = [_merge_adjacent_blocks(page) for page in body_pages if page]

    if len(body_pages) > _BODY_SLIDE_WARN_THRESHOLD:
        print(
            f"Warning: {len(body_pages)} body slides (>{_BODY_SLIDE_WARN_THRESHOLD}); "
            f"consider raising chars_per_slide in manifest (current {max_chars}).",
            file=sys.stderr,
            flush=True,
        )

    body_total = len(body_pages)

    slides: list[tuple[str, str]] = []
    slides.append((COVER_OUTPUT_FILENAME, _render_cover_slide(manifest, manifest_dir)))

    for index, blocks in enumerate(body_pages, start=1):
        filename = f"{index + 1:02d}.png"
        continues_paragraph = False
        if index > 1:
            previous_page = body_pages[index - 2]
            if previous_page and blocks:
                previous_last = previous_page[-1]
                first_block = blocks[0]
                continues_paragraph = (
                    previous_last.kind == "paragraph"
                    and first_block.kind == "paragraph"
                    and previous_last.source_id == first_block.source_id
                )
        html_doc = _render_body_page(
            header,
            blocks,
            index,
            body_total,
            nickname,
            continues_paragraph=continues_paragraph,
        )
        slides.append((filename, html_doc))

    end_page_num = body_total + 2
    slides.append((f"{end_page_num:02d}-end.png", _render_end_slide(manifest)))
    return slides, manifest_dir
