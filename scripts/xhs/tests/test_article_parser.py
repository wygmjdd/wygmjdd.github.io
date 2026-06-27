from __future__ import annotations

from pathlib import Path

import pytest

from scripts.xhs.xhs_cards.article_parser import (
    detect_embedded_images,
    parse_body_blocks,
    strip_body_for_xhs,
)
from scripts.wechat.normalize_article_footer import parse_frontmatter_markdown

SAMPLE = """---
title: 特斯拉与外星人
primary_category: reading-category
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


def test_parse_body_blocks_quote_and_paragraphs() -> None:
    post = parse_frontmatter_markdown(SAMPLE)
    body = strip_body_for_xhs(post.content)
    blocks = parse_body_blocks(body)
    assert len(blocks) == 3
    assert blocks[0].kind == "paragraph"
    assert blocks[1].kind == "quote"
    assert blocks[1].text == "引用内容在这里。"
    assert blocks[2].kind == "paragraph"


def test_detect_embedded_images() -> None:
    assert not detect_embedded_images("plain text")
    assert detect_embedded_images("![alt](/images/x.jpg)")
    assert detect_embedded_images('<figure class="figure-with-caption">')
