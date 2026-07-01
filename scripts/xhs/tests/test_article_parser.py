from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.xhs.xhs_cards.article_parser import load_manifest, strip_body_for_xhs
from scripts.xhs.xhs_cards.xhs_config import (
    SUPPORTED_MANIFEST_VERSION,
    enrich_manifest_from_article,
    load_category_titles,
    resolve_category_title,
    resolve_cta_theme,
)
from scripts.wechat.normalize_article_footer import parse_frontmatter_markdown

SAMPLE = """---
title: 特斯拉与外星人
primary_category: yue-du-shu-mu
---
正文第一段。

> 引用内容在这里。

正文第二段。 <small>（<a href="https://mp.weixin.qq.com/s/x" rel="noopener noreferrer">原文链接</a>，更新于2026-06-26。）</small>
"""


def test_strip_body_removes_source_link_footer() -> None:
    post = parse_frontmatter_markdown(SAMPLE)
    body = strip_body_for_xhs(post.content)
    assert "原文链接" not in body
    assert "正文第一段" in body
    assert "正文第二段" in body


def test_strip_inline_markdown_links() -> None:
    from scripts.xhs.xhs_cards.article_parser import strip_inline_markdown_links

    text = "除去前面的[工作](https://example.com/a)与[读书](https://example.com/b)之外。"
    assert strip_inline_markdown_links(text) == "除去前面的工作与读书之外。"


def test_strip_body_removes_inline_markdown_links() -> None:
    post = parse_frontmatter_markdown(
        """---
title: t
---
除去前面的[工作](https://example.com/a)之外。
"""
    )
    body = strip_body_for_xhs(post.content)
    assert body == "除去前面的工作之外。"
    assert "](http" not in body


def test_parse_body_blocks_quote_and_paragraphs() -> None:
    from scripts.xhs.xhs_cards.article_parser import parse_body_blocks

    post = parse_frontmatter_markdown(SAMPLE)
    body = strip_body_for_xhs(post.content)
    blocks = parse_body_blocks(body)
    assert len(blocks) == 3
    assert blocks[0].kind == "paragraph"
    assert blocks[1].kind == "quote"
    assert blocks[1].text == "引用内容在这里。"
    assert blocks[2].kind == "paragraph"


def test_detect_embedded_images() -> None:
    from scripts.xhs.xhs_cards.article_parser import detect_embedded_images

    assert not detect_embedded_images("plain text")
    assert detect_embedded_images("![alt](/images/x.jpg)")
    assert detect_embedded_images('<figure class="figure-with-caption">')


def test_load_manifest_rejects_unsupported_version(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"manifest_version": 99}), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported manifest_version"):
        load_manifest(path)


def test_load_manifest_accepts_current_version(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({"manifest_version": SUPPORTED_MANIFEST_VERSION, "source": "x.md"}),
        encoding="utf-8",
    )
    data = load_manifest(path)
    assert data["manifest_version"] == SUPPORTED_MANIFEST_VERSION


def test_resolve_cta_theme_from_config() -> None:
    assert resolve_cta_theme("yue-du-shu-mu") == "reading"
    assert resolve_cta_theme("zong-jie") == "summary"
    assert resolve_cta_theme("di-tie-ri-ji") == "life"
    assert resolve_cta_theme("unknown-slug") == "reading"


def test_resolve_category_title() -> None:
    titles = load_category_titles()
    if "yue-du-shu-mu" in titles:
        assert resolve_category_title("yue-du-shu-mu") == titles["yue-du-shu-mu"]


def test_enrich_manifest_fills_category_title_from_article() -> None:
    manifest = {"primary_category": "yue-du-shu-mu"}
    enriched = enrich_manifest_from_article(manifest, {})
    titles = load_category_titles()
    if "yue-du-shu-mu" in titles:
        assert enriched["category_title"] == titles["yue-du-shu-mu"]


def test_enrich_manifest_uses_article_metadata_slug() -> None:
    manifest: dict = {}
    enriched = enrich_manifest_from_article(
        manifest,
        {"primary_category": "yue-du-shu-mu", "title": "特斯拉与外星人"},
    )
    assert enriched["primary_category"] == "yue-du-shu-mu"
    titles = load_category_titles()
    if "yue-du-shu-mu" in titles:
        assert enriched["category_title"] == titles["yue-du-shu-mu"]


def test_enrich_manifest_keeps_explicit_category_title() -> None:
    manifest = {
        "primary_category": "yue-du-shu-mu",
        "category_title": "自定义标题",
    }
    enriched = enrich_manifest_from_article(manifest, {})
    assert enriched["category_title"] == "自定义标题"
