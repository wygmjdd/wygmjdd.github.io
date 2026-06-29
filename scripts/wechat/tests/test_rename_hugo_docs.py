from __future__ import annotations

from pathlib import Path

from scripts.wechat.rename_hugo_docs import RenameResult, rename_hugo_docs


def write_doc(path: Path, *, title: str, date: str, category: str, body: str = "Body") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"title: {title}\n"
        f"date: '{date}'\n"
        "weight: 1\n"
        f"primary_category: {category}\n"
        "---\n\n"
        f"{body}\n",
        encoding="utf-8",
    )


def test_dry_run_reports_renames_without_changing_files(tmp_path: Path) -> None:
    docs = tmp_path / "content" / "docs"
    old_doc = docs / "2026" / "06" / "subway-diary__post-b055ab191a.md"
    write_doc(
        old_doc,
        title="端午小记，什么都不做的三天",
        date="2026-06-22",
        category="subway-diary",
    )

    result = rename_hugo_docs(docs, apply=False)

    assert result == RenameResult(renamed=1, unchanged=0, skipped=0, collisions=0)
    assert old_doc.exists()
    assert not (
        docs / "2026" / "06" / "2026-06-22-duan-wu-xiao-ji-shen-subway-diary.md"
    ).exists()


def test_apply_renames_article_docs_and_preserves_content(tmp_path: Path) -> None:
    docs = tmp_path / "content" / "docs"
    old_doc = docs / "2026" / "06" / "subway-diary__post-b055ab191a.md"
    write_doc(
        old_doc,
        title="端午小记，什么都不做的三天",
        date="2026-06-22",
        category="subway-diary",
        body="Original body",
    )
    before = old_doc.read_text(encoding="utf-8")

    result = rename_hugo_docs(docs, apply=True)

    new_doc = docs / "2026" / "06" / "2026-06-22-duan-wu-xiao-ji-shen-subway-diary.md"
    assert result == RenameResult(renamed=1, unchanged=0, skipped=0, collisions=0)
    assert not old_doc.exists()
    assert new_doc.read_text(encoding="utf-8") == before


def test_rename_skips_indexes_and_hub_pages(tmp_path: Path) -> None:
    docs = tmp_path / "content" / "docs"
    write_doc(
        docs / "2026" / "06" / "_index.md",
        title="六月",
        date="2026-06-01",
        category="summary",
    )
    write_doc(
        docs / "hubs" / "summary.md",
        title="总结",
        date="2026-06-01",
        category="summary",
    )

    result = rename_hugo_docs(docs, apply=True)

    assert result == RenameResult(renamed=0, unchanged=0, skipped=2, collisions=0)
    assert (docs / "2026" / "06" / "_index.md").exists()
    assert (docs / "hubs" / "summary.md").exists()


def test_collision_appends_legacy_stem_suffix(tmp_path: Path) -> None:
    docs = tmp_path / "content" / "docs"
    first = docs / "2026" / "06" / "subway-diary__post-b055ab191a.md"
    second = docs / "2026" / "06" / "subway-diary__post-cafebabe00.md"
    for path, body in ((first, "First"), (second, "Second")):
        write_doc(
            path,
            title="端午小记，什么都不做的三天",
            date="2026-06-22",
            category="subway-diary",
            body=body,
        )

    result = rename_hugo_docs(docs, apply=True)

    assert result == RenameResult(renamed=2, unchanged=0, skipped=0, collisions=1)
    names = sorted(path.name for path in (docs / "2026" / "06").glob("*.md"))
    assert names == [
        "2026-06-22-duan-wu-xiao-ji-shen-subway-diary-cafebabe00.md",
        "2026-06-22-duan-wu-xiao-ji-shen-subway-diary.md",
    ]


def test_collision_suffix_files_are_stable_on_second_run(tmp_path: Path) -> None:
    docs = tmp_path / "content" / "docs"
    first = docs / "2026" / "06" / "subway-diary__post-b055ab191a.md"
    second = docs / "2026" / "06" / "subway-diary__post-cafebabe00.md"
    for path in (first, second):
        write_doc(
            path,
            title="端午小记，什么都不做的三天",
            date="2026-06-22",
            category="subway-diary",
        )

    rename_hugo_docs(docs, apply=True)
    result = rename_hugo_docs(docs, apply=False)

    assert result == RenameResult(renamed=0, unchanged=2, skipped=0, collisions=0)


def test_dry_run_counts_future_collisions(tmp_path: Path) -> None:
    docs = tmp_path / "content" / "docs"
    first = docs / "2026" / "06" / "subway-diary__post-b055ab191a.md"
    second = docs / "2026" / "06" / "subway-diary__post-cafebabe00.md"
    for path in (first, second):
        write_doc(
            path,
            title="端午小记，什么都不做的三天",
            date="2026-06-22",
            category="subway-diary",
        )

    result = rename_hugo_docs(docs, apply=False)

    assert result == RenameResult(renamed=2, unchanged=0, skipped=0, collisions=1)
    assert first.exists()
    assert second.exists()


def test_already_readable_files_are_unchanged(tmp_path: Path) -> None:
    docs = tmp_path / "content" / "docs"
    doc = docs / "2026" / "06" / "2026-06-22-duan-wu-xiao-ji-shen-subway-diary.md"
    write_doc(
        doc,
        title="端午小记，什么都不做的三天",
        date="2026-06-22",
        category="subway-diary",
    )

    result = rename_hugo_docs(docs, apply=True)

    assert result == RenameResult(renamed=0, unchanged=1, skipped=0, collisions=0)
    assert doc.exists()
