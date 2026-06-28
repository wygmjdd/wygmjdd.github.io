"""Parse Hugo article markdown for Xiaohongshu slide generation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from scripts.wechat.normalize_article_footer import (
    parse_frontmatter_markdown,
    strip_cta_html,
    strip_trailing_promo_lines,
)
from scripts.xhs.xhs_cards.xhs_config import REPO_ROOT, SUPPORTED_MANIFEST_VERSION

_INLINE_LINK_RE = re.compile(
    r' <small>（<a href="([^"]+)" rel="noopener noreferrer">原文链接</a>'
    r"(?:，更新于\d{4}-\d{2}-\d{2}。)?）</small>"
)
_INLINE_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((?:[^()\\]|\\.|[^()])*?\)")
_IMAGE_MARKDOWN_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")
_FIGURE_HTML_RE = re.compile(r"<figure\b", re.IGNORECASE)


@dataclass(frozen=True)
class ContentBlock:
    kind: Literal["paragraph", "quote"]
    text: str
    source_id: int = 0


@dataclass
class ParsedArticle:
    metadata: dict[str, Any]
    body: str
    blocks: list[ContentBlock]
    has_embedded_images: bool


def strip_inline_markdown_links(text: str) -> str:
    """Replace [anchor](url) with anchor text only."""
    return _INLINE_MARKDOWN_LINK_RE.sub(r"\1", text)


def strip_body_for_xhs(body: str) -> str:
    text = strip_cta_html(body)
    text = _INLINE_LINK_RE.sub("", text)
    text = strip_trailing_promo_lines(text)
    text = strip_inline_markdown_links(text)
    return text.strip()


def detect_embedded_images(body: str) -> bool:
    return bool(_IMAGE_MARKDOWN_RE.search(body) or _FIGURE_HTML_RE.search(body))


def parse_body_blocks(body: str) -> list[ContentBlock]:
    blocks: list[ContentBlock] = []
    lines = body.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while index < len(lines):
                current = lines[index]
                if current.strip().startswith(">"):
                    quote_lines.append(re.sub(r"^>\s?", "", current.strip()))
                    index += 1
                elif not current.strip() and quote_lines:
                    index += 1
                    break
                else:
                    break
            blocks.append(ContentBlock("quote", "\n".join(quote_lines).strip()))
            continue

        paragraph_lines: list[str] = []
        while index < len(lines):
            current = lines[index]
            if not current.strip():
                break
            if current.strip().startswith(">"):
                break
            paragraph_lines.append(current)
            index += 1
        blocks.append(ContentBlock("paragraph", "\n".join(paragraph_lines).strip()))
    return [block for block in blocks if block.text]


def parse_article_file(path: Path) -> ParsedArticle:
    raw = path.read_text(encoding="utf-8")
    post = parse_frontmatter_markdown(raw)
    body = strip_body_for_xhs(post.content)
    return ParsedArticle(
        metadata=post.metadata,
        body=body,
        blocks=parse_body_blocks(body),
        has_embedded_images=detect_embedded_images(post.content),
    )


def load_manifest(path: Path) -> dict[str, Any]:
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"manifest must be a JSON object: {path}")
    version = data.get("manifest_version", 1)
    if version != SUPPORTED_MANIFEST_VERSION:
        raise ValueError(
            f"Unsupported manifest_version {version!r} in {path}; "
            f"expected {SUPPORTED_MANIFEST_VERSION}"
        )
    return data


def merge_manifest_defaults(manifest: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    merged = dict(manifest)
    merged.setdefault("nickname", config.get("nickname", ""))
    merged.setdefault("bio", config.get("bio", ""))
    merged.setdefault("chars_per_slide", config.get("chars_per_slide", 340))
    return merged


def resolve_source_path(manifest: dict[str, Any], manifest_path: Path) -> Path:
    source = manifest.get("source")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("manifest missing source path")
    source_path = Path(source.strip())
    if source_path.is_absolute():
        return source_path
    return REPO_ROOT / source_path
