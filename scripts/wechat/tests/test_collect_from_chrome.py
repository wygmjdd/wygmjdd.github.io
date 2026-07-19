import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.wechat.article_metadata import ArticlePageMetadata
from scripts.wechat.update_manual.collect_from_chrome import (
    batch_entry,
    chrome_cutoff_timestamp,
    collect_new_articles,
    CollectedArticle,
    deduplicate_detected_articles,
    detect_article_category,
    is_wechat_article_url,
    load_article_key_cache,
    load_category_title_slugs,
    load_existing_article_keys,
    load_existing_source_urls,
    normalize_history_title,
    update_article_key_cache,
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


def test_load_existing_article_keys_reads_long_wechat_urls(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "sample.md").write_text(
        "---\n"
        "title: 纽带不止篮球\n"
        "source_url: >-\n"
        "  https://mp.weixin.qq.com/s?__biz=biz-id&mid=123&idx=1&sn=signature\n"
        "---\n\nbody\n",
        encoding="utf-8",
    )
    assert load_existing_article_keys(
        docs,
        cache_path=tmp_path / "missing-cache.yml",
    ) == {"biz-id|123|1|signature"}


def test_load_existing_article_keys_uses_cached_identity_for_existing_short_url(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    short_url = "https://mp.weixin.qq.com/s/short-link"
    (docs / "sample.md").write_text(
        f"---\ntitle: Sample\nsource_url: {short_url}\n---\n\nbody\n",
        encoding="utf-8",
    )
    cache = tmp_path / "article-keys.yml"
    cache.write_text(
        f"'{short_url}': biz-id|123|1|signature\n"
        "'https://mp.weixin.qq.com/s/not-in-site': biz-id|999|1|other\n",
        encoding="utf-8",
    )

    assert load_existing_article_keys(docs, cache_path=cache) == {
        "biz-id|123|1|signature",
    }


def test_update_article_key_cache_only_persists_short_urls(tmp_path: Path):
    cache = tmp_path / "article-keys.yml"
    articles = [
        CollectedArticle(
            url="https://mp.weixin.qq.com/s/short-link",
            title="短链接",
            visited_at=datetime.now(timezone.utc),
            article_key="biz-id|123|1|signature",
        ),
        CollectedArticle(
            url=(
                "https://mp.weixin.qq.com/s?__biz=biz-id&mid=124&idx=1&sn=long-signature"
            ),
            title="长链接",
            visited_at=datetime.now(timezone.utc),
            article_key="biz-id|124|1|long-signature",
        ),
    ]

    assert update_article_key_cache(cache, articles) == 1
    assert load_article_key_cache(cache) == {
        "https://mp.weixin.qq.com/s/short-link": "biz-id|123|1|signature",
    }
    assert update_article_key_cache(cache, articles) == 0


def test_existing_short_url_cache_blocks_same_article_long_url(monkeypatch, tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    short_url = "https://mp.weixin.qq.com/s/short-link"
    article_key = "biz-id|123|1|signature"
    (docs / "sample.md").write_text(
        f"---\ntitle: Existing\nsource_url: {short_url}\n---\n\nbody\n",
        encoding="utf-8",
    )
    cache = tmp_path / "article-keys.yml"
    cache.write_text(f"'{short_url}': {article_key}\n", encoding="utf-8")
    long_article = CollectedArticle(
        url=(
            "https://mp.weixin.qq.com/s?__biz=biz-id&mid=123&idx=1&sn=signature"
            "&scene=21"
        ),
        title="Existing",
        visited_at=datetime.now(timezone.utc),
    )
    monkeypatch.setattr(
        "scripts.wechat.update_manual.collect_from_chrome.query_wechat_articles",
        lambda _path, *, days, biz: [long_article],
    )

    existing_urls = load_existing_source_urls(docs)
    existing_keys = load_existing_article_keys(
        docs,
        cache_path=cache,
        source_urls=existing_urls,
    )
    collected = collect_new_articles(
        tmp_path / "unused-history",
        days=1,
        biz=None,
        existing=existing_urls,
        existing_keys=existing_keys,
    )

    assert collected == []


def test_cached_short_variant_is_skipped_without_metadata_lookup(monkeypatch, tmp_path: Path):
    article_key = "biz-id|123|1|signature"
    short_variant = "https://mp.weixin.qq.com/s/another-short-link"
    article = CollectedArticle(
        url=short_variant,
        title="Existing",
        visited_at=datetime.now(timezone.utc),
    )
    monkeypatch.setattr(
        "scripts.wechat.update_manual.collect_from_chrome.query_wechat_articles",
        lambda _path, *, days, biz: [article],
    )

    collected = collect_new_articles(
        tmp_path / "unused-history",
        days=1,
        biz=None,
        existing=set(),
        existing_keys={article_key},
        article_key_cache={short_variant: article_key},
    )

    assert collected == []


def test_main_skips_short_article_when_identity_lookup_fails(
    monkeypatch,
    tmp_path: Path,
    capsys,
):
    import scripts.wechat.update_manual.collect_from_chrome as mod

    def fail_detect(*_args, **_kwargs):
        raise ValueError("temporary response")

    def fail_write(*_args, **_kwargs):
        raise AssertionError("unexpected batch")

    article = CollectedArticle(
        url="https://mp.weixin.qq.com/s/unknown-short-link",
        title="暂时无法识别",
        visited_at=datetime.now(timezone.utc),
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    monkeypatch.setattr(mod, "DOCS_DIR", docs)
    monkeypatch.setattr(mod, "CATEGORIES_YML", tmp_path / "categories.yml")
    monkeypatch.setattr(mod, "ARTICLE_KEYS_YML", tmp_path / "article-keys.yml")
    monkeypatch.setattr(
        mod,
        "collect_new_articles",
        lambda *_args, **_kwargs: [article],
    )
    monkeypatch.setattr(
        mod,
        "detect_article_category",
        fail_detect,
    )
    monkeypatch.setattr(
        mod,
        "write_batch_json",
        fail_write,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["collect_from_chrome", "--history-path", str(tmp_path / "History")],
    )

    mod.main()

    captured = capsys.readouterr()
    assert "skipping until a stable identity can be read" in captured.err
    assert "No new WeChat articles remain after identity checks." in captured.out


def test_collect_new_articles_keeps_same_title_when_identity_is_unknown(
    monkeypatch,
    tmp_path: Path,
):
    article = CollectedArticle(
        url="https://mp.weixin.qq.com/s/short-link",
        title="纽带不止篮球",
        visited_at=datetime.now(timezone.utc),
    )
    monkeypatch.setattr(
        "scripts.wechat.update_manual.collect_from_chrome.query_wechat_articles",
        lambda _path, *, days, biz: [article],
    )

    assert collect_new_articles(
        tmp_path / "unused-history",
        days=1,
        biz=None,
        existing=set(),
        existing_keys=set(),
    ) == [article]


def test_collect_new_articles_deduplicates_tracking_url_variants(monkeypatch, tmp_path: Path):
    base = "https://mp.weixin.qq.com/s?__biz=biz-id&mid=123&idx=1&sn=signature"
    articles = [
        CollectedArticle(
            url=base + "&scene=21&poc_token=temporary",
            title="测试标题",
            visited_at=datetime.now(timezone.utc),
        ),
        CollectedArticle(
            url=base + "&scene=21",
            title="测试标题",
            visited_at=datetime.now(timezone.utc),
        ),
    ]
    monkeypatch.setattr(
        "scripts.wechat.update_manual.collect_from_chrome.query_wechat_articles",
        lambda _path, *, days, biz: articles,
    )

    collected = collect_new_articles(
        tmp_path / "unused-history",
        days=1,
        biz=None,
        existing=set(),
        existing_keys=set(),
    )

    assert len(collected) == 1
    assert collected[0].article_key == "biz-id|123|1|signature"


def test_detected_short_url_is_skipped_when_identity_already_exists():
    article = CollectedArticle(
        url="https://mp.weixin.qq.com/s/short-link",
        title="纽带不止篮球",
        visited_at=datetime.now(timezone.utc),
        article_key="biz-id|123|1|signature",
    )

    kept, skipped = deduplicate_detected_articles(
        [article],
        existing_keys={"biz-id|123|1|signature"},
    )

    assert kept == []
    assert skipped == [article]


def test_same_title_with_different_identities_is_preserved():
    articles = [
        CollectedArticle(
            url="https://mp.weixin.qq.com/s/first",
            title="相同标题",
            visited_at=datetime.now(timezone.utc),
            article_key="biz-id|123|1|first",
        ),
        CollectedArticle(
            url="https://mp.weixin.qq.com/s/second",
            title="相同标题",
            visited_at=datetime.now(timezone.utc),
            article_key="biz-id|124|1|second",
        ),
    ]

    kept, skipped = deduplicate_detected_articles(articles, existing_keys=set())

    assert kept == articles
    assert skipped == []


def test_chrome_cutoff_timestamp_grows_with_lookback_days():
    assert chrome_cutoff_timestamp(30) < chrome_cutoff_timestamp(7)


def test_normalize_history_title_collapses_whitespace():
    assert normalize_history_title("  hello   world  ") == "hello world"
    assert normalize_history_title(None) == ""


def test_load_category_title_slugs_maps_display_titles(tmp_path: Path):
    categories = tmp_path / "categories.yml"
    categories.write_text(
        "- slug: 30-fen-zhong-ri-ji\n  title: 30分钟日记\n",
        encoding="utf-8",
    )
    assert load_category_title_slugs(categories) == {
        "30分钟日记": "30-fen-zhong-ri-ji",
    }


def test_load_category_title_slugs_accepts_yaml_field_order(tmp_path: Path):
    categories = tmp_path / "categories.yml"
    categories.write_text(
        "- title: 30分钟日记\n  slug: 30-fen-zhong-ri-ji\n",
        encoding="utf-8",
    )
    assert load_category_title_slugs(categories) == {
        "30分钟日记": "30-fen-zhong-ri-ji",
    }


def test_detected_category_overrides_fallback_slug():
    article = CollectedArticle(
        url="https://mp.weixin.qq.com/s/abc",
        title="测试标题",
        visited_at=datetime.now(timezone.utc),
    )
    article = detect_article_category(
        article,
        {"30分钟日记": "30-fen-zhong-ri-ji"},
        fetch_metadata=lambda _url: ArticlePageMetadata(
            album_title="30 分钟日记",
            article_key="biz-id|123|1|signature",
        ),
    )
    assert article.article_key == "biz-id|123|1|signature"
    assert batch_entry(article, slug="di-tie-ri-ji") == {
        "title": "测试标题",
        "slug": "30-fen-zhong-ri-ji",
        "url": "https://mp.weixin.qq.com/s/abc",
    }


def test_unknown_category_keeps_fallback_slug():
    article = CollectedArticle(
        url="https://mp.weixin.qq.com/s/abc",
        title="测试标题",
        visited_at=datetime.now(timezone.utc),
    )
    article = detect_article_category(
        article,
        {"30分钟日记": "30-fen-zhong-ri-ji"},
        fetch_metadata=lambda _url: ArticlePageMetadata(album_title="新的合集"),
    )
    assert article.category_title == "新的合集"
    assert article.category_slug is None
    assert batch_entry(article, slug="di-tie-ri-ji")["slug"] == "di-tie-ri-ji"


def test_disabled_category_detection_still_enriches_article_identity():
    article = CollectedArticle(
        url="https://mp.weixin.qq.com/s/short-link",
        title="测试标题",
        visited_at=datetime.now(timezone.utc),
    )

    article = detect_article_category(
        article,
        {"30分钟日记": "30-fen-zhong-ri-ji"},
        fetch_metadata=lambda _url: ArticlePageMetadata(
            album_title="30分钟日记",
            article_key="biz-id|123|1|signature",
        ),
        include_category=False,
    )

    assert article.article_key == "biz-id|123|1|signature"
    assert article.category_title is None
    assert batch_entry(article, slug="di-tie-ri-ji")["slug"] == "di-tie-ri-ji"


def test_disabled_category_detection_reuses_known_identity_without_fetching():
    def fail_fetch(_url: str) -> ArticlePageMetadata:
        raise AssertionError("unexpected metadata fetch")

    article = CollectedArticle(
        url="https://mp.weixin.qq.com/s/short-link",
        title="测试标题",
        visited_at=datetime.now(timezone.utc),
        category_title="旧合集",
        category_slug="old-category",
        article_key="biz-id|123|1|signature",
    )

    detected = detect_article_category(
        article,
        {},
        fetch_metadata=fail_fetch,
        include_category=False,
    )

    assert detected.article_key == article.article_key
    assert detected.category_title is None
    assert detected.category_slug is None
