from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.xhs.xhs_cards.article import (
    COVER_AI_FILENAME,
    COVER_BG_FILENAME,
    COVER_OUTPUT_FILENAME,
    _CSS_PATH,
    prepare_cover_ai,
    render_article_slides,
    sync_cover_deliverables,
)


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
    cover_ai = tmp_path / COVER_AI_FILENAME
    cover_ai.write_bytes(b"\x89PNG\r\n\x1a\n")

    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "test-article",
        "original_title": "测试标题",
        "xhs_title": "小红书标题",
        "primary_category": "reading-category",
        "cover_ai": COVER_AI_FILENAME,
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "cta_line2": "关注理由测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 270,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return tmp_path


def test_render_article_slides_cover_body_end(manifest_dir: Path) -> None:
    slides, output_dir = render_article_slides(manifest_dir / "manifest.json")
    assert output_dir == manifest_dir
    filenames = [name for name, _ in slides]
    assert filenames[0] == COVER_OUTPUT_FILENAME
    assert filenames[-1].endswith("-end.png")

    cover_html = slides[0][1]
    assert "小红书标题" in cover_html
    assert "阅读书目" not in cover_html
    assert "测试标题" not in cover_html
    assert "cover-title-card" in cover_html
    assert '<div class="slide-footer' not in cover_html

    body_html = slides[1][1]
    assert "第一段内容" in body_html
    assert "引用一句" in body_html
    assert "frame-header" in body_html
    assert 'class="slide-frame' not in body_html
    assert "article-p-start" in body_html
    assert '<div class="slide-footer">' in body_html
    assert "@我要改名叫嘟嘟" in body_html
    assert "footer-page" in body_html

    end_html = slides[-1][1]
    assert "共鸣句测试" in end_html
    assert "关注理由测试" not in end_html
    assert "@我要改名叫嘟嘟" in end_html
    assert '<div class="slide-footer' not in end_html


def test_summary_article_label_overrides_stale_reading_theme(tmp_path: Path) -> None:
    article_path = tmp_path / "article.md"
    article_path.write_text(
        "---\n"
        "title: 2025年终总结（下），认识自己后的依然做自己\n"
        "primary_category: summary\n"
        "---\n"
        "正文内容。\n",
        encoding="utf-8",
    )
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "summary-article",
        "original_title": "2025年终总结（下），认识自己后的依然做自己",
        "xhs_title": "在我之外，还有一个安静看着我的我",
        "primary_category": "summary",
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    slides, _ = render_article_slides(manifest_path)

    cover_html = slides[0][1]
    end_html = slides[-1][1]
    assert '<div class="cover-kicker">年度总结</div>' in cover_html
    assert '<div class="end-theme">年度总结</div>' in end_html
    assert '<div class="cover-kicker">读书感悟</div>' not in cover_html
    assert '<div class="end-theme">读书感悟</div>' not in end_html


def test_summary_article_allows_explicit_cta_label(tmp_path: Path) -> None:
    article_path = tmp_path / "article.md"
    article_path.write_text(
        "---\n"
        "title: 2024年读完书籍（下）\n"
        "primary_category: summary\n"
        "---\n"
        "正文内容。\n",
        encoding="utf-8",
    )
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "summary-reading-list",
        "original_title": "2024年读完书籍（下）",
        "xhs_title": "这些书留在了这一年里",
        "primary_category": "summary",
        "cta_theme": "summary",
        "cta_label": "读书感悟",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    slides, _ = render_article_slides(manifest_path)

    cover_html = slides[0][1]
    end_html = slides[-1][1]
    assert '<div class="cover-kicker">读书感悟</div>' in cover_html
    assert '<div class="end-theme">读书感悟</div>' in end_html
    assert '<div class="cover-kicker">年度总结</div>' not in cover_html
    assert '<div class="end-theme">年度总结</div>' not in end_html


def test_cover_css_keeps_title_thumbnail_readable() -> None:
    css = _CSS_PATH.read_text(encoding="utf-8")

    assert ".cover-title-card" in css
    assert ".cover-kicker" in css
    assert "font-size: 86px;" in css
    assert "background: transparent;" in css
    assert "min-height: 780px;" in css


def test_quote_css_uses_editorial_note_treatment() -> None:
    css = _CSS_PATH.read_text(encoding="utf-8")

    assert ".article-quote::before" in css
    assert "background: var(--quote-surface);" in css
    assert "border-left: 0;" in css
    assert "font-size: 29px;" in css


def test_quote_layout_estimate_matches_quote_css() -> None:
    from scripts.xhs.xhs_cards.article_layout import (
        QUOTE_FONT,
        QUOTE_LINE_HEIGHT,
        QUOTE_PADDING_HORIZONTAL,
        QUOTE_PADDING_VERTICAL,
    )

    assert QUOTE_FONT == 29
    assert QUOTE_LINE_HEIGHT == 1.78
    assert QUOTE_PADDING_VERTICAL == 24
    assert QUOTE_PADDING_HORIZONTAL == 42


def test_prepare_cover_ai_from_legacy_cover_bg(tmp_path: Path) -> None:
    legacy = tmp_path / COVER_BG_FILENAME
    legacy.write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {"cover_bg": COVER_BG_FILENAME}

    ai_path = prepare_cover_ai(tmp_path, manifest)

    assert ai_path == tmp_path / COVER_AI_FILENAME
    assert ai_path.is_file()


def test_render_article_slides_uses_default_cover_without_cover_ai(tmp_path: Path) -> None:
    article_path = tmp_path / "article.md"
    article_path.write_text(
        "---\n"
        "title: 无底图测试\n"
        "primary_category: summary\n"
        "---\n"
        "正文内容。\n",
        encoding="utf-8",
    )
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "default-cover",
        "original_title": "无底图测试",
        "xhs_title": "没有 AI 底图也能生成文字封面",
        "primary_category": "summary",
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    slides, _ = render_article_slides(manifest_path)

    cover_html = slides[0][1]
    assert "没有 AI 底图也能生成文字封面" in cover_html
    assert "background-image" not in cover_html


def test_render_article_slides_errors_when_declared_cover_ai_is_missing(tmp_path: Path) -> None:
    article_path = tmp_path / "article.md"
    article_path.write_text(
        "---\n"
        "title: 缺失底图测试\n"
        "primary_category: summary\n"
        "---\n"
        "正文内容。\n",
        encoding="utf-8",
    )
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "missing-cover",
        "original_title": "缺失底图测试",
        "xhs_title": "声明了底图就不能静默丢失",
        "primary_category": "summary",
        "cover_ai": COVER_AI_FILENAME,
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="Declared cover background missing"):
        render_article_slides(manifest_path)


def test_sync_cover_deliverables_copies_rendered_cover(tmp_path: Path) -> None:
    cover_out = tmp_path / COVER_OUTPUT_FILENAME
    cover_out.write_bytes(b"rendered-cover")
    bg_path = tmp_path / COVER_BG_FILENAME
    bg_path.write_bytes(b"old-bg")

    sync_cover_deliverables(tmp_path)

    assert bg_path.read_bytes() == b"rendered-cover"


def test_render_article_slides_uses_browser_paginator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.xhs.xhs_cards import article as article_module
    from scripts.xhs.xhs_cards.article_parser import ContentBlock

    article_path = tmp_path / "article.md"
    article_path.write_text(
        "---\n"
        "title: 分页路径测试\n"
        "primary_category: summary\n"
        "---\n"
        "原始正文不应该直接进入 body。\n",
        encoding="utf-8",
    )
    cover_ai = tmp_path / COVER_AI_FILENAME
    cover_ai.write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "browser-path",
        "original_title": "分页路径测试",
        "xhs_title": "浏览器分页路径测试",
        "primary_category": "summary",
        "cover_ai": COVER_AI_FILENAME,
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    def fake_paginate(
        blocks: list[ContentBlock],
        render_page_html,
        *,
        max_chars: int,
    ) -> list[list[ContentBlock]]:
        assert max_chars == 120
        assert blocks[0].text == "原始正文不应该直接进入 body。"
        return [[ContentBlock("paragraph", "浏览器分页被调用。", 0)]]

    monkeypatch.setattr(article_module, "paginate_blocks_with_browser", fake_paginate)

    slides, _ = article_module.render_article_slides(manifest_path)
    body_html = slides[1][1]

    assert "浏览器分页被调用。" in body_html
    assert "原始正文不应该直接进入 body。" not in body_html


def test_render_article_slides_continues_long_paragraph_without_indent(tmp_path: Path) -> None:
    article_path = tmp_path / "article.md"
    sentence = "我观察自己的情绪起伏，担忧焦虑证明我害怕失去某种东西。"
    article_path.write_text(
        "---\n"
        "title: 长段落测试\n"
        "primary_category: summary\n"
        "---\n"
        f"{sentence * 48}\n",
        encoding="utf-8",
    )
    cover_ai = tmp_path / COVER_AI_FILENAME
    cover_ai.write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "long-paragraph",
        "original_title": "长段落测试",
        "xhs_title": "在我之外，还有一个安静看着我的我",
        "primary_category": "summary",
        "cover_ai": COVER_AI_FILENAME,
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    slides, _ = render_article_slides(manifest_path)
    body_slides = [
        (name, html)
        for name, html in slides
        if name != COVER_OUTPUT_FILENAME and not name.endswith("-end.png")
    ]

    assert len(body_slides) >= 2
    assert any("article-p-continue" in html for _, html in body_slides[1:])


def test_render_article_slides_browser_paginated_body_does_not_overflow(tmp_path: Path) -> None:
    article_path = tmp_path / "article.md"
    sentence = "这是一段足够长的中文句子，用来撑高真实浏览器分页并检查底部裁切。"
    article_path.write_text(
        "---\n"
        "title: 裁切测试\n"
        "primary_category: summary\n"
        "---\n"
        f"{sentence * 44}\n",
        encoding="utf-8",
    )
    cover_ai = tmp_path / COVER_AI_FILENAME
    cover_ai.write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "overflow-check",
        "original_title": "裁切测试",
        "xhs_title": "在我之外，还有一个安静看着我的我",
        "primary_category": "summary",
        "cover_ai": COVER_AI_FILENAME,
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    slides, _ = render_article_slides(manifest_path)
    body_slides = [
        (name, html)
        for name, html in slides
        if name != COVER_OUTPUT_FILENAME and not name.endswith("-end.png")
    ]

    from scripts.xhs.xhs_cards.article_browser_paginator import _BODY_FITS_JS
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        browser_page = browser.new_page(viewport={"width": 1080, "height": 1440})
        try:
            for name, html in body_slides:
                browser_page.set_content(html, wait_until="load")
                assert browser_page.evaluate(_BODY_FITS_JS), f"{name} overflowed"
        finally:
            browser.close()
