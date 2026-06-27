from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.xhs.xhs_cards.article import render_article_slides


@pytest.fixture
def manifest_dir(tmp_path: Path) -> Path:
    article_path = tmp_path / "article.md"
    article_path.write_text(
        """---
title: 测试标题
primary_category: reading-category
---
第一段内容。

> 引用一句。

第二段内容。
""",
        encoding="utf-8",
    )
    cover_bg = tmp_path / "cover-bg.png"
    cover_bg.write_bytes(b"\x89PNG\r\n\x1a\n")

    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "test-article",
        "original_title": "测试标题",
        "xhs_title": "小红书标题",
        "cover_subtitle": "测试标题",
        "primary_category": "reading-category",
        "category_title": "阅读书目",
        "cover_bg": "cover-bg.png",
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "cta_line2": "关注理由测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 200,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return tmp_path


def test_render_article_slides_cover_body_end(manifest_dir: Path) -> None:
    slides, output_dir = render_article_slides(manifest_dir / "manifest.json")
    assert output_dir == manifest_dir
    filenames = [name for name, _ in slides]
    assert filenames[0] == "01-cover.png"
    assert filenames[-1].endswith("-end.png")

    cover_html = slides[0][1]
    assert "小红书标题" in cover_html
    assert "阅读书目" in cover_html

    body_html = slides[1][1]
    assert "第一段内容" in body_html
    assert "引用一句" in body_html

    end_html = slides[-1][1]
    assert "共鸣句测试" in end_html
    assert "@我要改名叫嘟嘟" in end_html
