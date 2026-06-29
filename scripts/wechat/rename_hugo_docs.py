#!/usr/bin/env python3
"""Rename existing Hugo docs to readable date/title/category filenames."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from scripts.wechat.migrate_jekyll_to_hugo_book import (
    hugo_doc_filename,
    legacy_hash_suffix,
    parse_frontmatter_markdown,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOCS_ROOT = ROOT / "content" / "docs"


@dataclass(frozen=True)
class RenameResult:
    renamed: int = 0
    unchanged: int = 0
    skipped: int = 0
    collisions: int = 0


def is_article_doc(path: Path) -> bool:
    if path.name == "_index.md":
        return False
    return "hubs" not in path.parts


def date_to_iso(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        stripped = value.strip().strip("'\"")
        if len(stripped) >= 10:
            return stripped[:10]
    return None


def target_path_for_doc(path: Path) -> Path | None:
    post = parse_frontmatter_markdown(path.read_text(encoding="utf-8"))
    date_iso = date_to_iso(post.get("date"))
    title = post.get("title")
    category = post.get("primary_category")
    if not date_iso or not isinstance(title, str) or not isinstance(category, str):
        return None
    return path.with_name(hugo_doc_filename(date_iso, title, category))


def collision_path(target: Path, original: Path, reserved: set[Path]) -> Path:
    suffix = legacy_hash_suffix(original.name)
    candidate = target.with_name(f"{target.stem}-{suffix}.md")
    if candidate == original or (not candidate.exists() and candidate not in reserved):
        return candidate

    index = 2
    while True:
        numbered = target.with_name(f"{target.stem}-{suffix}-{index}.md")
        if numbered == original or (not numbered.exists() and numbered not in reserved):
            return numbered
        index += 1


def is_stable_collision_name(path: Path, target: Path) -> bool:
    if path.suffix != ".md" or path.parent != target.parent:
        return False
    return path.stem.startswith(f"{target.stem}-")


def doc_sort_key(path: Path) -> tuple[str, int, str]:
    target = target_path_for_doc(path) if is_article_doc(path) else None
    target_name = target.name if target else path.name
    priority = 0 if path.name == target_name else 1
    return (str(path.parent / target_name), priority, str(path))


def rename_hugo_docs(docs_root: Path = DEFAULT_DOCS_ROOT, *, apply: bool = False) -> RenameResult:
    renamed = 0
    unchanged = 0
    skipped = 0
    collisions = 0
    reserved: set[Path] = set()

    for path in sorted(docs_root.rglob("*.md"), key=doc_sort_key):
        if not is_article_doc(path):
            skipped += 1
            continue

        target = target_path_for_doc(path)
        if target is None:
            skipped += 1
            continue

        if path == target:
            unchanged += 1
            reserved.add(target)
            continue

        if is_stable_collision_name(path, target) and target.exists():
            unchanged += 1
            reserved.add(path)
            continue

        if target.exists() or target in reserved:
            target = collision_path(target, path, reserved)
            collisions += 1

        renamed += 1
        reserved.add(target)
        if apply:
            path.rename(target)

    return RenameResult(
        renamed=renamed,
        unchanged=unchanged,
        skipped=skipped,
        collisions=collisions,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-root",
        type=Path,
        default=DEFAULT_DOCS_ROOT,
        help="Hugo docs root to migrate (default: content/docs)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually rename files. Without this flag, only report counts.",
    )
    args = parser.parse_args()

    result = rename_hugo_docs(args.docs_root, apply=args.apply)
    mode = "applied" if args.apply else "dry-run"
    print(
        f"{mode}: renamed={result.renamed} unchanged={result.unchanged} "
        f"skipped={result.skipped} collisions={result.collisions}"
    )


if __name__ == "__main__":
    main()
