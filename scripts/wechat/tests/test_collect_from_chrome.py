from datetime import datetime, timezone
from pathlib import Path

from scripts.wechat.update_manual.collect_from_chrome import (
    batch_entry,
    chrome_cutoff_timestamp,
    CollectedArticle,
    is_wechat_article_url,
    load_existing_source_urls,
    normalize_history_title,
)


def test_is_wechat_article_url_accepts_short_and_long_links():
    assert is_wechat_article_url("https://mp.weixin.qq.com/s/ZTCRX8DJrHESQ5VsHP2B0g")
    assert is_wechat_article_url(
        "http://mp.weixin.qq.com/s?__biz=MjM5ODczOTMzMA==&mid=2247484118&idx=1"
    )
    assert not is_wechat_article_url("https://mp.weixin.qq.com/mp/homepage")


def test_load_existing_source_urls_reads_front_matter(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "sample.md").write_text(
        "---\ntitle: t\nsource_url: https://mp.weixin.qq.com/s/abc\n---\n\nbody\n",
        encoding="utf-8",
    )
    existing = load_existing_source_urls(docs)
    assert existing == {"https://mp.weixin.qq.com/s/abc"}


def test_chrome_cutoff_timestamp_grows_with_lookback_days():
    assert chrome_cutoff_timestamp(30) < chrome_cutoff_timestamp(7)


def test_normalize_history_title_collapses_whitespace():
    assert normalize_history_title("  hello   world  ") == "hello world"
    assert normalize_history_title(None) == ""


def test_batch_entry_includes_title_slug_url():
    article = CollectedArticle(
        url="https://mp.weixin.qq.com/s/abc",
        title="测试标题",
        visited_at=datetime.now(timezone.utc),
    )
    assert batch_entry(article, slug="subway-diary") == {
        "title": "测试标题",
        "slug": "subway-diary",
        "url": "https://mp.weixin.qq.com/s/abc",
    }
