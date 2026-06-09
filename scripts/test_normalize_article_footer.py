from datetime import date, datetime

from normalize_article_footer import (
    build_source_link_suffix,
    format_date_from_meta,
    normalize_source_link,
    transform_body,
)

SOURCE_URL = "https://mp.weixin.qq.com/s?x=1&b=2"
HREF = "https://mp.weixin.qq.com/s?x=1&amp;b=2"
OLD_SUFFIX = (
    f' <small>（<a href="{HREF}" rel="noopener noreferrer">原文链接</a>）</small>'
)
NEW_SUFFIX = (
    f' <small>（<a href="{HREF}" rel="noopener noreferrer">原文链接</a>，更新于2019-06-15。）</small>'
)


def test_format_date_from_meta_parses_string():
    assert format_date_from_meta({"date": "2019-06-15"}) == "2019-06-15"


def test_format_date_from_meta_parses_datetime_types():
    assert format_date_from_meta({"date": date(2019, 6, 15)}) == "2019-06-15"
    assert format_date_from_meta({"date": datetime(2019, 6, 15, 12, 0)}) == "2019-06-15"


def test_format_date_from_meta_returns_none_for_missing_or_invalid():
    assert format_date_from_meta({}) is None
    assert format_date_from_meta({"date": "June 15, 2019"}) is None


def test_build_source_link_suffix_with_and_without_date():
    assert build_source_link_suffix(HREF, "2019-06-15") == NEW_SUFFIX
    assert build_source_link_suffix(HREF, None) == OLD_SUFFIX


def test_normalize_source_link_appends_new_link_with_date():
    body = "Last paragraph."
    new_body, changed = normalize_source_link(body, SOURCE_URL, "2019-06-15")
    assert changed is True
    assert new_body == f"Last paragraph.{NEW_SUFFIX}"


def test_normalize_source_link_appends_without_date_when_missing():
    body = "Last paragraph."
    new_body, changed = normalize_source_link(body, SOURCE_URL, None)
    assert changed is True
    assert new_body == f"Last paragraph.{OLD_SUFFIX}"


def test_normalize_source_link_upgrades_old_format():
    body = f"Last paragraph.{OLD_SUFFIX}"
    new_body, changed = normalize_source_link(body, SOURCE_URL, "2019-06-15")
    assert changed is True
    assert new_body == f"Last paragraph.{NEW_SUFFIX}"


def test_normalize_source_link_is_idempotent_for_new_format():
    body = f"Last paragraph.{NEW_SUFFIX}"
    new_body, changed = normalize_source_link(body, SOURCE_URL, "2019-06-15")
    assert changed is False
    assert new_body == body


def test_normalize_source_link_updates_date_when_frontmatter_changes():
    body = f"Last paragraph.{NEW_SUFFIX}"
    new_body, changed = normalize_source_link(body, SOURCE_URL, "2020-01-02")
    expected = (
        f' <small>（<a href="{HREF}" rel="noopener noreferrer">原文链接</a>，更新于2020-01-02。）</small>'
    )
    assert changed is True
    assert new_body == f"Last paragraph.{expected}"


def test_normalize_source_link_skips_without_source_url():
    body = "Last paragraph."
    new_body, changed = normalize_source_link(body, None, "2019-06-15")
    assert changed is False
    assert new_body == body


def test_transform_body_upgrades_existing_footer():
    body = f"Paragraph one.\n\nParagraph two.{OLD_SUFFIX}"
    new_body, changed = transform_body(body, SOURCE_URL, "2019-06-15")
    assert changed is True
    assert new_body.endswith(NEW_SUFFIX)


def test_transform_body_second_run_is_unchanged():
    body = f"Paragraph one.{NEW_SUFFIX}"
    new_body, changed = transform_body(body, SOURCE_URL, "2019-06-15")
    assert changed is False
    assert new_body == body
