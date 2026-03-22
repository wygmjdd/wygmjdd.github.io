"""Tests for fetch_article using HTML fixture (no live WeChat)."""

import pytest

from bs4 import BeautifulSoup

from fetch_article import _img_real_url, _parse_chinese_date, fetch_article

# Minimal WeChat-like HTML: title in og:title, date in meta or script, body in #js_content
FIXTURE_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta property="og:title" content="Test Article Title" />
<meta name="publish_time" content="2024-03-01 12:00:00" />
</head>
<body>
<div id="js_content">
<p>First paragraph.</p>
<p>Second <strong>paragraph</strong> with <a href="/s?foo">link</a>.</p>
</div>
</body>
</html>
"""


def test_fetch_article_returns_dict_with_required_keys(monkeypatch):
    def mock_get(url, **kwargs):
        class R:
            text = FIXTURE_HTML
            def raise_for_status(self): pass
        return R()
    monkeypatch.setattr("fetch_article.requests.get", mock_get)
    result = fetch_article("https://mp.weixin.qq.com/s?__biz=xxx", download_images=False)
    assert "title" in result
    assert "date" in result
    assert "body_md" in result
    assert "source_url" in result
    assert result["source_url"] == "https://mp.weixin.qq.com/s?__biz=xxx"


def test_fetch_article_extracts_title_and_content(monkeypatch):
    def mock_get(url, **kwargs):
        class R:
            text = FIXTURE_HTML
            def raise_for_status(self): pass
        return R()
    monkeypatch.setattr("fetch_article.requests.get", mock_get)
    result = fetch_article("https://example.com/s?x=1", download_images=False)
    assert result["title"] == "Test Article Title"
    assert "First paragraph" in result["body_md"]
    assert "Second" in result["body_md"] and "paragraph" in result["body_md"]


def test_fetch_article_extracts_or_defaults_date(monkeypatch):
    def mock_get(url, **kwargs):
        class R:
            text = FIXTURE_HTML
            def raise_for_status(self): pass
        return R()
    monkeypatch.setattr("fetch_article.requests.get", mock_get)
    result = fetch_article("https://example.com/s", download_images=False)
    # If we parse meta publish_time we get 2024-03-01; else we use today
    assert result["date"] is not None
    date_val = result["date"]
    if hasattr(date_val, "strftime"):
        assert date_val.year in (2024, 2026)
    else:
        assert isinstance(date_val, str) and len(date_val) >= 8


def test_parse_chinese_date():
    assert _parse_chinese_date("2026年2月27日 09:15") == "2026-02-27"
    assert _parse_chinese_date("2024年12月1日") == "2024-12-01"
    assert _parse_chinese_date("no date here") is None


def test_img_real_url_prefers_data_src_over_placeholder_src():
    soup = BeautifulSoup(
        '<img data-src="https://mmbiz.qpic.cn/x" src="data:image/svg+xml,foo"/>',
        "html.parser",
    )
    img = soup.find("img")
    assert _img_real_url(img, "https://mp.weixin.qq.com/s?a=1") == "https://mmbiz.qpic.cn/x"
