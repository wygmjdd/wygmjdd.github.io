#!/usr/bin/env python3
"""Migrate Jekyll-style posts into Hugo hugo-book content/docs tree.

Reads posts from ``_archive/legacy-jekyll/_rehydrated_posts`` (or ``_posts`` fallback)
and categories from ``data/categories.yml``. Override source dir with env
``WYGMJDD_POSTS_DIR`` if needed.

Posts that share the same canonical ``source_url`` (after HTML unescape and stripping
``#fragment``) collapse to a single output page; the winner uses the same tie-break
as before (higher filename revision, then longer body).

Output layout (newest year/month first via weight):

    content/docs/
      _index.md
      hubs/{slug}.md   # hub pages per data/categories.yml (bookHidden)
      {YYYY}/_index.md
      {YYYY}/{MM}/_index.md
      {YYYY}/{MM}/{YYYY-MM-DD}-{title-prefix-pinyin}-{category}.md
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from pypinyin import lazy_pinyin

ROOT = Path(__file__).resolve().parents[2]
LEGACY_JEKYLL = ROOT / "_archive" / "legacy-jekyll"
CATEGORIES_FILE = ROOT / "data" / "categories.yml"
OUT_DOCS = ROOT / "content" / "docs"
REHYDRATED_DIR = LEGACY_JEKYLL / "_rehydrated_posts"
LEGACY_POSTS_DIR = LEGACY_JEKYLL / "_posts"

CATEGORY_ALIASES: dict[str, str] = {
    "yuedushumu": "reading-category",
    "year-end-summary": "summary",
}

FALLBACK_CATEGORY = "uncategorized"
FALLBACK_TITLE = "未分类"

# Ascending Hugo weight = earlier in menu; use high anchor so newer dates sort first.
_YEAR_WEIGHT_BASE = 4000
_MAX_POST_DATE_ORDINAL = date(2100, 12, 31).toordinal()

DATE_FILENAME_RE = re.compile(
    r"^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})-(?P<slug>.+)\.md$",
    re.IGNORECASE,
)
POST_NUM_RE = re.compile(r"post-(\d+)", re.IGNORECASE)
STEM_WITH_DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")
WECHAT_HASH_RE = re.compile(r"post-([a-f0-9]{8,12})", re.IGNORECASE)


def canonical_source_url(url: str) -> str:
    """Match migrate.py / rehydrate_posts: stable key for WeChat article URLs."""
    return html.unescape(url.strip()).split("#", 1)[0]


def is_better_candidate(
    rev: int,
    body_len: int,
    path_name: str,
    prev_rev: int,
    prev_len: int,
    prev_path: str,
) -> bool:
    if rev > prev_rev:
        return True
    if rev < prev_rev:
        return False
    if body_len > prev_len:
        return True
    if body_len < prev_len:
        return False
    return False


class MarkdownPost:
    """YAML front matter + Markdown body (no external frontmatter parser)."""

    __slots__ = ("metadata", "content")

    def __init__(self, metadata: dict[str, Any], content: str) -> None:
        self.metadata = metadata
        self.content = content

    def get(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)


# revision, body_len, post, path_name, category, out_slug — pick best duplicate
CandidateRow = tuple[int, int, MarkdownPost, str, str, str]


def parse_frontmatter_markdown(text: str) -> MarkdownPost:
    """Parse leading --- YAML --- block; body is the rest of the file."""
    if text.startswith("\ufeff"):
        text = text[1:]
    stripped = text.lstrip("\n\r")
    if not stripped.startswith("---"):
        return MarkdownPost({}, text)

    lines = stripped.splitlines()
    if not lines or lines[0].strip() != "---":
        return MarkdownPost({}, text)

    end_idx: int | None = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return MarkdownPost({}, text)

    fm_block = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :])
    if body.startswith("\n"):
        body = body[1:]

    meta_raw = yaml.safe_load(fm_block)
    meta: dict[str, Any] = meta_raw if isinstance(meta_raw, dict) else {}
    return MarkdownPost(meta, body)


def posts_source_dir() -> Path:
    override = os.environ.get("WYGMJDD_POSTS_DIR", "").strip()
    if override:
        path = Path(override)
        if not path.is_dir():
            raise FileNotFoundError(f"WYGMJDD_POSTS_DIR is not a directory: {path}")
        return path
    if REHYDRATED_DIR.is_dir() and any(REHYDRATED_DIR.glob("*.md")):
        return REHYDRATED_DIR
    return LEGACY_POSTS_DIR


def count_doc_articles(docs_root: Path) -> int:
    count = 0
    for path in docs_root.rglob("*.md"):
        if path.name == "_index.md":
            continue
        if "hubs" in path.parts:
            continue
        count += 1
    return count


def refuse_destructive_rebuild(posts_dir: Path, source_count: int) -> None:
    if not OUT_DOCS.is_dir():
        return
    existing = count_doc_articles(OUT_DOCS)
    if existing < 50 or source_count >= 50:
        return
    raise SystemExit(
        f"Refusing full rebuild: source has {source_count} post(s) but "
        f"{OUT_DOCS.relative_to(ROOT)} already has {existing} article(s). "
        "For incremental batches use migrate_jekyll_to_hugo_book --merge with "
        "WYGMJDD_POSTS_DIR pointing at the batch rehydrated files only."
    )


def output_slug_and_revision(filename: str) -> tuple[str, int]:
    """Map rehydrated names like post-2-2.md onto canonical slug post-2 with revision 2."""
    stem = Path(filename).stem
    match = STEM_WITH_DATE_PREFIX_RE.match(stem)
    if not match:
        return stem.replace("/", "-"), 0
    rest = match.group(2)
    parts = rest.split("-")
    if not parts or parts[0] != "post":
        return rest.replace("/", "-"), 0
    if len(parts) == 1:
        return "post", 0
    if len(parts) == 2:
        return f"post-{parts[1]}", 0
    if parts[-1].isdigit():
        return f"post-{parts[1]}", int(parts[-1])
    return rest, 0


def load_category_titles() -> dict[str, str]:
    raw = yaml.safe_load(CATEGORIES_FILE.read_text(encoding="utf-8"))
    titles: dict[str, str] = {}
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            slug = item.get("slug")
            title = item.get("title")
            if isinstance(slug, str) and isinstance(title, str):
                titles[slug.strip()] = title.strip()
        if not titles:
            raise ValueError("categories.yml list must contain {slug, title} entries")
        return titles
    if isinstance(raw, dict):
        for key, value in raw.items():
            if not isinstance(key, str) or not isinstance(value, str):
                continue
            titles[key.strip()] = value.strip()
        if not titles:
            raise ValueError("categories.yml mapping must be non-empty")
        return titles
    raise ValueError("categories.yml must be a list of {slug, title} or a mapping")


def normalize_category_slug(raw: str) -> str:
    return CATEGORY_ALIASES.get(raw.strip(), raw.strip())


def pick_root_category(categories: Any, allowed: set[str]) -> str:
    if isinstance(categories, str):
        categories = [categories]
    if not isinstance(categories, list):
        return FALLBACK_CATEGORY
    for item in categories:
        if not isinstance(item, str):
            continue
        slug = normalize_category_slug(item)
        if slug in allowed:
            return slug
    return FALLBACK_CATEGORY


def parse_date(post: MarkdownPost, filename: str) -> tuple[int, int, int]:
    date_val = post.get("date")
    if isinstance(date_val, str):
        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", date_val.strip())
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
    match = DATE_FILENAME_RE.match(filename)
    if match:
        return int(match.group("y")), int(match.group("m")), int(match.group("d"))
    return 1970, 1, 1


def slug_from_filename(name: str) -> str:
    match = DATE_FILENAME_RE.match(name)
    if match:
        return match.group("slug")
    return Path(name).stem


def post_menu_weight(year: int, month: int, day: int, slug: str) -> int:
    """Newer posts first (ascending menu order) with stable tie-break."""
    ordinal = date(year, month, day).toordinal()
    base = _MAX_POST_DATE_ORDINAL - ordinal
    tie = 0
    match = POST_NUM_RE.search(slug)
    if match:
        tie = int(match.group(1))
    else:
        tie = day
    return base * 10_000 + tie


def title_for_post(post: MarkdownPost, slug: str) -> str:
    title = post.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    return slug.replace("-", " ").strip() or "无标题"


def title_prefix_to_pinyin(title: str, limit: int = 5) -> str:
    chars: list[str] = []
    for char in title.strip():
        if char.isspace() or not char.isalnum():
            continue
        chars.append(char)
        if len(chars) >= limit:
            break

    prefix = "".join(chars) or "untitled"
    parts: list[str] = []
    for part in lazy_pinyin(prefix):
        cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", part).strip("-").lower()
        if cleaned:
            parts.append(cleaned)
    return "-".join(parts) or "untitled"


def hugo_doc_filename(date_iso: str, title: str, category: str) -> str:
    title_slug = title_prefix_to_pinyin(title)
    category_slug = re.sub(r"[^a-zA-Z0-9-]+", "-", category.strip()).strip("-").lower()
    if not category_slug:
        category_slug = FALLBACK_CATEGORY
    return f"{date_iso}-{title_slug}-{category_slug}.md"


def legacy_hash_suffix(src_name: str) -> str:
    stem = Path(src_name).stem
    match = WECHAT_HASH_RE.search(stem)
    if match:
        return match.group(1)
    date_match = STEM_WITH_DATE_PREFIX_RE.match(stem)
    if date_match:
        stem = date_match.group(2)
    return re.sub(r"[^a-zA-Z0-9-]+", "-", stem).strip("-") or "post"


def frontmatter_source_url(path: Path) -> str | None:
    try:
        post = parse_frontmatter_markdown(path.read_text(encoding="utf-8"))
    except OSError:
        return None
    source_url = post.get("source_url")
    if isinstance(source_url, str) and source_url.strip():
        return canonical_source_url(source_url)
    return None


def resolve_doc_output_path(
    month_dir: Path,
    *,
    desired_filename: str,
    source_url: str | None,
    src_name: str,
) -> Path:
    desired_path = month_dir / desired_filename
    if not source_url:
        if not desired_path.exists():
            return desired_path
        return desired_path.with_name(f"{desired_path.stem}-{legacy_hash_suffix(src_name)}.md")

    canonical = canonical_source_url(source_url)
    same_source_paths: list[Path] = []
    for existing in month_dir.glob("*.md"):
        if existing.name == "_index.md":
            continue
        if frontmatter_source_url(existing) != canonical:
            continue
        same_source_paths.append(existing)

    if same_source_paths:
        for existing in same_source_paths:
            if existing != desired_path:
                existing.unlink()
        return desired_path

    if not desired_path.exists():
        return desired_path
    return desired_path.with_name(f"{desired_path.stem}-{legacy_hash_suffix(src_name)}.md")


def dump_post_md(meta: dict[str, Any], body: str) -> str:
    header = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).rstrip()
    text = f"---\n{header}\n---\n"
    if body.strip():
        text += "\n" + body.rstrip() + "\n"
    else:
        text += "\n"
    return text


def write_index(path: Path, title: str, weight: int, book_collapse: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    meta: dict[str, Any] = {"title": title, "weight": weight}
    if book_collapse:
        meta["bookCollapseSection"] = True
    header = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).rstrip()
    path.write_text(f"---\n{header}\n---\n\n", encoding="utf-8")


def write_toc_hub_pages() -> None:
    """Hidden index pages used by layouts/partials/docs/inject/toc-before.html."""
    hubs = OUT_DOCS / "hubs"
    hubs.mkdir(parents=True, exist_ok=True)
    for cat_slug, title in load_category_titles().items():
        meta: dict[str, Any] = {
            "title": title,
            "list_category": cat_slug,
            "bookHidden": True,
            "bookSearchExclude": True,
            "weight": 9999,
        }
        body = (
            "按年月浏览请使用左侧目录；本页列出该分类下的全部文章（按日期倒序）。\n"
        )
        (hubs / f"{cat_slug}.md").write_text(
            dump_post_md(meta, body),
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate Jekyll-style posts into Hugo content/docs.")
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Write or update only posts from the source dir; do not wipe content/docs.",
    )
    args = parser.parse_args()

    posts_dir = posts_source_dir()
    if not posts_dir.is_dir():
        raise FileNotFoundError(f"Missing posts directory: {posts_dir}")

    source_files = sorted(posts_dir.glob("*.md"))
    if not source_files:
        raise SystemExit(f"No markdown posts found in {posts_dir}")

    if args.merge:
        OUT_DOCS.mkdir(parents=True, exist_ok=True)
    else:
        refuse_destructive_rebuild(posts_dir, len(source_files))
        if OUT_DOCS.exists():
            shutil.rmtree(OUT_DOCS)
        OUT_DOCS.mkdir(parents=True, exist_ok=True)

    category_titles = load_category_titles()
    allowed_roots = set(category_titles.keys()) | {FALLBACK_CATEGORY}

    by_source_url: dict[str, CandidateRow] = {}
    by_category_slug: dict[tuple[str, str], CandidateRow] = {}

    for path in source_files:
        raw_text = path.read_text(encoding="utf-8")
        post = parse_frontmatter_markdown(raw_text)

        category = pick_root_category(post.get("categories"), allowed_roots)
        if category == FALLBACK_CATEGORY:
            category_titles.setdefault(FALLBACK_CATEGORY, FALLBACK_TITLE)

        out_slug, revision = output_slug_and_revision(path.name)
        if posts_dir == LEGACY_POSTS_DIR:
            out_slug = slug_from_filename(path.name)
            revision = 0

        body_len = len(post.content.strip())
        row: CandidateRow = (revision, body_len, post, path.name, category, out_slug)

        su_raw = post.get("source_url")
        if isinstance(su_raw, str) and su_raw.strip():
            ukey = canonical_source_url(su_raw)
            prev = by_source_url.get(ukey)
            if prev is None or is_better_candidate(
                revision, body_len, path.name, prev[0], prev[1], prev[3]
            ):
                by_source_url[ukey] = row
        else:
            sk = (category, out_slug)
            prev = by_category_slug.get(sk)
            if prev is None or is_better_candidate(
                revision, body_len, path.name, prev[0], prev[1], prev[3]
            ):
                by_category_slug[sk] = row

    merged: list[CandidateRow] = list(by_source_url.values()) + list(
        by_category_slug.values()
    )

    candidates: dict[tuple[str, str], CandidateRow] = {}
    for row in merged:
        _, _, _, src_name, category, out_slug = row
        key = (category, out_slug)
        prev = candidates.get(key)
        if prev is None or is_better_candidate(
            row[0], row[1], row[3], prev[0], prev[1], prev[3]
        ):
            candidates[key] = row

    seen_years: set[int] = set()
    seen_year_month: set[tuple[int, int]] = set()

    for (category, out_slug), (_, _, post, src_name, _, _) in sorted(candidates.items()):
        year, month, day = parse_date(post, src_name)
        date_iso = f"{year:04d}-{month:02d}-{day:02d}"
        title = title_for_post(post, out_slug)
        weight = post_menu_weight(year, month, day, out_slug)

        source_url = post.get("source_url")
        if not isinstance(source_url, str) or not source_url.strip():
            source_url = None
        else:
            source_url = source_url.strip()

        meta = {
            "title": title,
            "date": date_iso,
            "weight": weight,
            "primary_category": category,
        }
        if source_url:
            meta["source_url"] = source_url

        new_body = dump_post_md(meta, post.content)
        month_dir = OUT_DOCS / f"{year:04d}" / f"{month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)
        out_path = resolve_doc_output_path(
            month_dir,
            desired_filename=hugo_doc_filename(date_iso, title, category),
            source_url=source_url,
            src_name=src_name,
        )
        out_path.write_text(new_body, encoding="utf-8")

        seen_years.add(year)
        seen_year_month.add((year, month))

    if args.merge:
        root_index = OUT_DOCS / "_index.md"
        if not root_index.is_file():
            write_index(root_index, "文章", 1)
        hubs_dir = OUT_DOCS / "hubs"
        if not hubs_dir.is_dir() or not any(hubs_dir.glob("*.md")):
            write_toc_hub_pages()
    else:
        write_index(OUT_DOCS / "_index.md", "文章", 1)
        write_toc_hub_pages()

    months_by_year: dict[int, list[int]] = defaultdict(list)
    for y, m in seen_year_month:
        months_by_year[y].append(m)
    for y in months_by_year:
        months_by_year[y].sort(reverse=True)

    for year in sorted(seen_years, reverse=True):
        year_index = OUT_DOCS / f"{year:04d}" / "_index.md"
        if args.merge and year_index.is_file():
            continue
        year_weight = _YEAR_WEIGHT_BASE - year
        write_index(
            year_index,
            f"{year}年",
            year_weight,
            book_collapse=True,
        )

    for year in sorted(seen_years, reverse=True):
        for month in months_by_year[year]:
            month_index = OUT_DOCS / f"{year:04d}" / f"{month:02d}" / "_index.md"
            if args.merge and month_index.is_file():
                continue
            month_weight = 100 - month
            write_index(
                month_index,
                f"{month:02d}月",
                month_weight,
            )

    mode = "merge" if args.merge else "full rebuild"
    print(f"Source: {posts_dir} ({mode})")
    print(f"Wrote {len(candidates)} posts under {OUT_DOCS}")


if __name__ == "__main__":
    main()
