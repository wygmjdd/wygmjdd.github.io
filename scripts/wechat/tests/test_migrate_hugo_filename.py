from __future__ import annotations

import sys
from pathlib import Path

import pytest

from scripts.wechat.migrate_jekyll_to_hugo_book import hugo_doc_filename


def test_hugo_doc_filename_uses_date_title_prefix_and_category() -> None:
    assert (
        hugo_doc_filename(
            date_iso="2026-06-22",
            title="端午小记，什么都不做的三天",
            category="subway-diary",
        )
        == "2026-06-22-duan-wu-xiao-ji-shen-subway-diary.md"
    )


def test_hugo_doc_filename_keeps_short_titles_short() -> None:
    assert (
        hugo_doc_filename(
            date_iso="2026-06-22",
            title="端午小记",
            category="subway-diary",
        )
        == "2026-06-22-duan-wu-xiao-ji-subway-diary.md"
    )


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
        "- slug: subway-diary\n"
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

    new_doc = docs / "2026" / "06" / "2026-06-22-duan-wu-xiao-ji-shen-subway-diary.md"
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
        "- slug: subway-diary\n"
        "  title: 地铁日记\n",
        encoding="utf-8",
    )
    source_url = "https://mp.weixin.qq.com/s/ex1x2IfLUMwt3mLDU2CTQA"
    new_doc = month_dir / "2026-06-22-duan-wu-xiao-ji-shen-subway-diary.md"
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
        "- slug: subway-diary\n"
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
        "2026-06-22-duan-wu-xiao-ji-shen-subway-diary-post-two.md",
        "2026-06-22-duan-wu-xiao-ji-shen-subway-diary.md",
    ]
    assert "First body" in month_files[1].read_text(encoding="utf-8")
    assert "Second body" in month_files[0].read_text(encoding="utf-8")
