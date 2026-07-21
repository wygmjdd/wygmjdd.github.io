from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

from scripts.wechat.migrate_jekyll_to_hugo_book import (
    MarkdownPost,
    hugo_doc_filename,
    parse_date,
)


def test_hugo_doc_filename_uses_date_title_prefix_and_category() -> None:
    assert (
        hugo_doc_filename(
            date_iso="2026-06-22",
            title="端午小记，什么都不做的三天",
            category="di-tie-ri-ji",
        )
        == "2026-06-22-di-tie-ri-ji-duan-wu-xiao-ji-shen-me-dou-bu.md"
    )


def test_hugo_doc_filename_keeps_short_titles_short() -> None:
    assert (
        hugo_doc_filename(
            date_iso="2026-06-22",
            title="端午小记",
            category="di-tie-ri-ji",
        )
        == "2026-06-22-di-tie-ri-ji-duan-wu-xiao-ji.md"
    )


def test_hugo_doc_filename_truncates_long_titles_to_eight_chars() -> None:
    assert (
        hugo_doc_filename(
            date_iso="2026-06-28",
            title="得知邻居家孩子高考成绩被屏蔽，我对《了凡四训》的理解更深了一点",
            category="30-fen-zhong-ri-ji",
        )
        == "2026-06-28-30-fen-zhong-ri-ji-de-zhi-lin-ju-jia-hai-zi-gao.md"
    )


def test_parse_date_rejects_future_front_matter_date() -> None:
    post = MarkdownPost({"date": "2041-03-21"}, "Body")

    with pytest.raises(ValueError, match="future dates are not allowed"):
        parse_date(post, "post.md", today=date(2026, 7, 21))


def test_parse_date_rejects_invalid_calendar_date() -> None:
    post = MarkdownPost({"date": "2026-02-30"}, "Body")

    with pytest.raises(ValueError, match="expected a real YYYY-MM-DD date"):
        parse_date(post, "post.md", today=date(2026, 7, 21))


def test_parse_date_rejects_implausibly_old_date() -> None:
    post = MarkdownPost({"date": "1970-01-01"}, "Body")

    with pytest.raises(ValueError, match="dates before 2000-01-01 are not allowed"):
        parse_date(post, "post.md", today=date(2026, 7, 21))


def test_merge_rejects_future_date_before_creating_year_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import scripts.wechat.migrate_jekyll_to_hugo_book as mod

    posts = tmp_path / "posts"
    docs = tmp_path / "content" / "docs"
    categories = tmp_path / "categories.yml"
    posts.mkdir()
    categories.write_text(
        "- slug: zong-jie\n"
        "  title: 总结\n",
        encoding="utf-8",
    )
    (posts / "2033-01-01-post-future.md").write_text(
        "---\n"
        "title: Future article\n"
        "date: '2041-03-21'\n"
        "categories:\n"
        "  - zong-jie\n"
        "---\n\n"
        "Body\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "OUT_DOCS", docs)
    monkeypatch.setattr(mod, "CATEGORIES_FILE", categories)
    monkeypatch.setenv("WYGMJDD_POSTS_DIR", str(posts))
    monkeypatch.setattr(sys, "argv", ["migrate_jekyll_to_hugo_book", "--merge"])

    with pytest.raises(ValueError, match="future dates are not allowed"):
        mod.main()

    assert not (docs / "2041").exists()


def test_merge_moves_existing_source_url_to_readable_filename(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import scripts.wechat.migrate_jekyll_to_hugo_book as mod

    posts = tmp_path / "posts"
    docs = tmp_path / "content" / "docs"
    categories = tmp_path / "categories.yml"
    posts.mkdir()
    (docs / "2026" / "06").mkdir(parents=True)
    categories.write_text(
        "- slug: di-tie-ri-ji\n"
        "  title: 地铁日记\n",
        encoding="utf-8",
    )
    source_url = "https://mp.weixin.qq.com/s/ex1x2IfLUMwt3mLDU2CTQA"
    old_doc = docs / "2026" / "06" / "subway-diary__post-b055ab191a.md"
    old_doc.write_text(
        "---\n"
        "title: 端午小记，什么都不做的三天\n"
        "date: '2026-06-22'\n"
        "primary_category: subway-diary\n"
        f"source_url: {source_url}\n"
        "---\n\n"
        "Old body\n",
        encoding="utf-8",
    )
    (posts / "2033-01-01-post-b055ab191a.md").write_text(
        "---\n"
        "title: 端午小记，什么都不做的三天\n"
        "date: '2026-06-22'\n"
        "categories:\n"
        "  - subway-diary\n"
        f"source_url: {source_url}\n"
        "---\n\n"
        "New body\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "OUT_DOCS", docs)
    monkeypatch.setattr(mod, "CATEGORIES_FILE", categories)
    monkeypatch.setenv("WYGMJDD_POSTS_DIR", str(posts))
    monkeypatch.setattr(sys, "argv", ["migrate_jekyll_to_hugo_book", "--merge"])

    mod.main()

    new_doc = docs / "2026" / "06" / "2026-06-22-di-tie-ri-ji-duan-wu-xiao-ji-shen-me-dou-bu.md"
    assert new_doc.is_file()
    assert "New body" in new_doc.read_text(encoding="utf-8")
    assert not old_doc.exists()


def test_merge_removes_stale_same_source_file_when_readable_file_exists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import scripts.wechat.migrate_jekyll_to_hugo_book as mod

    posts = tmp_path / "posts"
    docs = tmp_path / "content" / "docs"
    categories = tmp_path / "categories.yml"
    posts.mkdir()
    month_dir = docs / "2026" / "06"
    month_dir.mkdir(parents=True)
    categories.write_text(
        "- slug: di-tie-ri-ji\n"
        "  title: 地铁日记\n",
        encoding="utf-8",
    )
    source_url = "https://mp.weixin.qq.com/s/ex1x2IfLUMwt3mLDU2CTQA"
    new_doc = month_dir / "2026-06-22-di-tie-ri-ji-duan-wu-xiao-ji-shen-me-dou-bu.md"
    stale_doc = month_dir / "subway-diary__post-b055ab191a.md"
    for path, body in ((new_doc, "Existing body"), (stale_doc, "Stale body")):
        path.write_text(
            "---\n"
            "title: 端午小记，什么都不做的三天\n"
            "date: '2026-06-22'\n"
            "primary_category: subway-diary\n"
            f"source_url: {source_url}\n"
            "---\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
    (posts / "2033-01-01-post-b055ab191a.md").write_text(
        "---\n"
        "title: 端午小记，什么都不做的三天\n"
        "date: '2026-06-22'\n"
        "categories:\n"
        "  - subway-diary\n"
        f"source_url: {source_url}\n"
        "---\n\n"
        "New body\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "OUT_DOCS", docs)
    monkeypatch.setattr(mod, "CATEGORIES_FILE", categories)
    monkeypatch.setenv("WYGMJDD_POSTS_DIR", str(posts))
    monkeypatch.setattr(sys, "argv", ["migrate_jekyll_to_hugo_book", "--merge"])

    mod.main()

    assert new_doc.is_file()
    assert "New body" in new_doc.read_text(encoding="utf-8")
    assert not stale_doc.exists()


def test_merge_keeps_distinct_posts_when_readable_names_collide_without_source_url(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import scripts.wechat.migrate_jekyll_to_hugo_book as mod

    posts = tmp_path / "posts"
    docs = tmp_path / "content" / "docs"
    categories = tmp_path / "categories.yml"
    posts.mkdir()
    categories.write_text(
        "- slug: di-tie-ri-ji\n"
        "  title: 地铁日记\n",
        encoding="utf-8",
    )
    for name, body in (
        ("2026-06-22-post-one.md", "First body"),
        ("2026-06-22-post-two.md", "Second body"),
    ):
        (posts / name).write_text(
            "---\n"
            "title: 端午小记，什么都不做的三天\n"
            "date: '2026-06-22'\n"
            "categories:\n"
            "  - subway-diary\n"
            "---\n\n"
            f"{body}\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "OUT_DOCS", docs)
    monkeypatch.setattr(mod, "CATEGORIES_FILE", categories)
    monkeypatch.setenv("WYGMJDD_POSTS_DIR", str(posts))
    monkeypatch.setattr(sys, "argv", ["migrate_jekyll_to_hugo_book", "--merge"])

    mod.main()

    month_files = sorted((docs / "2026" / "06").glob("2026-06-22-*.md"))
    assert [path.name for path in month_files] == [
        "2026-06-22-di-tie-ri-ji-duan-wu-xiao-ji-shen-me-dou-bu-post-two.md",
        "2026-06-22-di-tie-ri-ji-duan-wu-xiao-ji-shen-me-dou-bu.md",
    ]
    assert "First body" in month_files[1].read_text(encoding="utf-8")
    assert "Second body" in month_files[0].read_text(encoding="utf-8")
