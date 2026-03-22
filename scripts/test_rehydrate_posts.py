import yaml

from pathlib import Path

import pytest

from rehydrate_posts import dedupe_skipped_log_on_disk, read_front_matter, write_rehydrated_post


def test_read_front_matter_parses_source_url_and_categories(tmp_path: Path):
    p = tmp_path / "a.md"
    p.write_text(
        "---\nsource_url: https://mp.weixin.qq.com/s?x=1\ncategories:\n  - cat-a\n  - cat-b\n---\n\nBody\n",
        encoding="utf-8",
    )
    fm = read_front_matter(p)
    assert fm.source_url == "https://mp.weixin.qq.com/s?x=1"
    assert fm.categories == ["cat-a", "cat-b"]


def test_dedupe_skipped_log_merges_same_url(tmp_path: Path):
    log = tmp_path / "skipped.yml"
    log.write_text(
        "- path: a.md\n"
        "  source_url: http://x?s=1&amp;b=2\n"
        "  reason: short\n"
        "- path: b.md\n"
        "  source_url: http://x?s=1&b=2\n"
        "  reason: longer reason wins here\n",
        encoding="utf-8",
    )
    n = dedupe_skipped_log_on_disk(log)
    assert n == 1
    text = log.read_text(encoding="utf-8")
    assert text.count("source_url:") == 1
    assert "longer reason wins" in text


def test_write_rehydrated_post_keeps_categories_and_source_url(tmp_path: Path):
    out_dir = tmp_path / "out"
    article = {"title": "New Title", "date": "2024-03-01", "body_md": "Hello **world**"}
    out_path = write_rehydrated_post(
        out_dir=out_dir,
        original_filename="2033-07-01-post-2.md",
        article=article,
        categories=["30min-diary"],
        source_url="https://mp.weixin.qq.com/s?x=1",
    )
    text = out_path.read_text(encoding="utf-8")
    assert text.startswith("---")
    fm_text = text.split("---", 2)[1]
    fm = yaml.safe_load(fm_text)
    assert fm["categories"] == ["30min-diary"]
    assert fm["source_url"] == "https://mp.weixin.qq.com/s?x=1"
    assert fm["title"] == "New Title"
    assert fm["date"] == "2024-03-01"
    assert "Hello" in text

