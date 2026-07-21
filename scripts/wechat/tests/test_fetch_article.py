"""Tests for fetch_article using HTML fixture (no live WeChat)."""

import pytest
from bs4 import BeautifulSoup

from scripts.wechat.article_metadata import (
    extract_album_title,
    extract_article_key,
    extract_article_key_from_url,
    fetch_article_metadata,
)
from scripts.wechat.fetch_article import (
    _extract_date,
    _get_html,
    _img_real_url,
    _parse_chinese_date,
    fetch_article,
)

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
<script>
window.articleData = {
  reportOpt: {
    biz: 'biz-id',
    mid: '123',
    idx: '1',
    sn: 'signature'
  },
  appmsgalbuminfo: {
    album_id: '123',
    title: '30分钟日记'
  }
};
</script>
</body>
</html>
"""


def test_fetch_article_returns_dict_with_required_keys(monkeypatch):
    def mock_get(url, **kwargs):
        class R:
            text = FIXTURE_HTML
            def raise_for_status(self): pass
        return R()
    monkeypatch.setattr("scripts.wechat.fetch_article.requests.get", mock_get)
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
    monkeypatch.setattr("scripts.wechat.fetch_article.requests.get", mock_get)
    result = fetch_article("https://example.com/s?x=1", download_images=False)
    assert result["title"] == "Test Article Title"
    assert "First paragraph" in result["body_md"]
    assert "Second" in result["body_md"] and "paragraph" in result["body_md"]


def test_extract_album_title_from_wechat_page_data():
    assert extract_album_title(FIXTURE_HTML) == "30分钟日记"


def test_extract_album_title_accepts_quoted_json_keys():
    page_data = '{"appmsgalbuminfo":{"album_id":"123","title":"30分钟日记"}}'
    assert extract_album_title(page_data) == "30分钟日记"
    assert extract_album_title('{"tag_name":"生活日记"}') == "生活日记"


def test_extract_album_title_decodes_javascript_unicode_escapes():
    page_data = (
        r'{"appmsgalbuminfo":{"title":'
        r'"\u0033\u0030\u5206\u949f\u65e5\u8bb0"}}'
    )
    assert extract_album_title(page_data) == "30分钟日记"


def test_extract_article_key_from_url_ignores_tracking_parameters():
    url = (
        "https://mp.weixin.qq.com/s?__biz=biz-id&mid=123&idx=1&sn=signature"
        "&scene=21&poc_token=temporary"
    )
    assert extract_article_key_from_url(url) == "biz-id|123|1|signature"


def test_extract_article_key_from_wechat_page_data():
    assert extract_article_key(FIXTURE_HTML) == "biz-id|123|1|signature"


def test_fetch_article_metadata_retries_response_without_identity(monkeypatch):
    class Headers:
        @staticmethod
        def get_content_charset():
            return "utf-8"

    class Response:
        headers = Headers()

        def __init__(self, body: str):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return self.body.encode("utf-8")

    responses = iter([Response("<html></html>"), Response(FIXTURE_HTML)])
    monkeypatch.setattr(
        "scripts.wechat.article_metadata.urlopen",
        lambda _request, *, timeout: next(responses),
    )
    monkeypatch.setattr("scripts.wechat.article_metadata.time.sleep", lambda _seconds: None)

    metadata = fetch_article_metadata("https://mp.weixin.qq.com/s/short", attempts=2)

    assert metadata.article_key == "biz-id|123|1|signature"
    assert metadata.album_title == "30分钟日记"


def test_fetch_article_metadata_fails_after_identity_retries(monkeypatch):
    class Headers:
        @staticmethod
        def get_content_charset():
            return "utf-8"

    class Response:
        headers = Headers()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        @staticmethod
        def read():
            return b"<html></html>"

    monkeypatch.setattr(
        "scripts.wechat.article_metadata.urlopen",
        lambda _request, *, timeout: Response(),
    )
    monkeypatch.setattr("scripts.wechat.article_metadata.time.sleep", lambda _seconds: None)

    with pytest.raises(ValueError, match="stable article identity"):
        fetch_article_metadata("https://mp.weixin.qq.com/s/short", attempts=2)


def test_get_html_uses_browser_headers_and_rejects_generic_title(monkeypatch):
    request_kwargs = {}

    def mock_get(url, **kwargs):
        request_kwargs.update(kwargs)

        class R:
            text = "<html><head><title>微信公众平台</title></head></html>"

            def raise_for_status(self):
                pass

        return R()

    monkeypatch.setattr("scripts.wechat.fetch_article.requests.get", mock_get)
    monkeypatch.setattr(
        "scripts.wechat.fetch_article._fetch_html_playwright",
        lambda _url: FIXTURE_HTML,
    )

    assert _get_html("https://mp.weixin.qq.com/s/abc") == FIXTURE_HTML
    assert request_kwargs["headers"]["Referer"] == "https://mp.weixin.qq.com/"
    assert "Mozilla/5.0" in request_kwargs["headers"]["User-Agent"]


def test_fetch_article_extracts_or_defaults_date(monkeypatch):
    def mock_get(url, **kwargs):
        class R:
            text = FIXTURE_HTML
            def raise_for_status(self): pass
        return R()
    monkeypatch.setattr("scripts.wechat.fetch_article.requests.get", mock_get)
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


def test_extract_date_ignores_unlabelled_ten_digit_article_id():
    soup = BeautifulSoup(
        '<script>window.articleData = { mid: "2247488053" };</script>',
        "html.parser",
    )

    assert _extract_date(soup) != "2041-03-21"


def test_extract_date_accepts_named_script_timestamp():
    soup = BeautifulSoup(
        '<script>window.articleData = { "create_time": "1709251200" };</script>',
        "html.parser",
    )

    assert _extract_date(soup) == "2024-03-01"


def test_extract_date_rejects_future_metadata():
    soup = BeautifulSoup(
        '<meta name="publish_time" content="2041-03-21 12:00:00" />',
        "html.parser",
    )

    with pytest.raises(ValueError, match="future dates are not allowed"):
        _extract_date(soup)


def test_extract_date_rejects_future_named_script_timestamp():
    soup = BeautifulSoup(
        '<script>window.articleData = { create_time: "2247488053" };</script>',
        "html.parser",
    )

    with pytest.raises(ValueError, match="future dates are not allowed"):
        _extract_date(soup)


def test_img_real_url_prefers_data_src_over_placeholder_src():
    soup = BeautifulSoup(
        '<img data-src="https://mmbiz.qpic.cn/x" src="data:image/svg+xml,foo"/>',
        "html.parser",
    )
    img = soup.find("img")
    assert _img_real_url(img, "https://mp.weixin.qq.com/s?a=1") == "https://mmbiz.qpic.cn/x"
