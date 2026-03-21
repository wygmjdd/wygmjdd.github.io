"""
Rehydrate already-generated Jekyll posts by reading `source_url` from front matter,
fetching the original WeChat article content, and writing a new, complete markdown
post into a separate output directory (leaving original `_posts` untouched).
"""

from __future__ import annotations

import argparse
import html
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LEGACY_JEKYLL = REPO_ROOT / "_archive" / "legacy-jekyll"
DEFAULT_POSTS_DIR = LEGACY_JEKYLL / "_posts"
DEFAULT_OUT_DIR = LEGACY_JEKYLL / "_rehydrated_posts"
DEFAULT_LOG_PATH = REPO_ROOT / "scripts" / "rehydrate_skipped.yml"


@dataclass(frozen=True)
class FrontMatter:
    title: str | None
    date: str | None
    categories: list[str]
    source_url: str


def _split_front_matter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        raise ValueError("Missing YAML front matter (file must start with '---').")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid YAML front matter (missing closing '---').")
    _empty, fm, body = parts[0], parts[1], parts[2]
    return fm.strip(), body.lstrip("\n")


def read_front_matter(path: Path) -> FrontMatter:
    fm_text, _body = _split_front_matter(path.read_text(encoding="utf-8"))
    data = yaml.safe_load(fm_text) or {}
    if not isinstance(data, dict):
        raise ValueError("Front matter YAML must be a mapping.")

    source_url = data.get("source_url")
    if not isinstance(source_url, str) or not source_url.strip():
        raise ValueError("Front matter must include non-empty 'source_url'.")
    source_url = html.unescape(source_url.strip())

    categories_raw = data.get("categories") or []
    if isinstance(categories_raw, str):
        categories = [categories_raw]
    elif isinstance(categories_raw, list):
        categories = [str(x) for x in categories_raw if str(x).strip()]
    else:
        categories = []

    title = data.get("title")
    date = data.get("date")
    return FrontMatter(
        title=str(title) if isinstance(title, str) else None,
        date=str(date) if isinstance(date, (str, int, float)) else None,
        categories=categories,
        source_url=source_url.strip(),
    )


def write_rehydrated_post(
    *,
    out_dir: Path,
    original_filename: str,
    article: dict,
    categories: list[str],
    source_url: str,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = original_filename
    target = out_dir / base
    n = 1
    while target.exists():
        n += 1
        stem, suffix = Path(base).stem, Path(base).suffix
        target = out_dir / f"{stem}-{n}{suffix}"

    front_matter = {
        "title": article.get("title", ""),
        "date": article.get("date", ""),
        "categories": categories,
        "source_url": source_url,
    }
    fm_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    body = (article.get("body_md") or "").rstrip()
    target.write_text(f"---\n{fm_str}---\n\n{body}\n", encoding="utf-8")
    return target


def iter_post_files(posts_dir: Path) -> list[Path]:
    if not posts_dir.exists():
        return []
    return sorted([p for p in posts_dir.glob("*.md") if p.is_file()])


def _append_skipped(log_path: Path, entry: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict] = []
    if log_path.exists():
        try:
            loaded = yaml.safe_load(log_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                existing = loaded
        except Exception:
            existing = []
    existing.append(entry)
    log_path.write_text(
        yaml.dump(existing, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _sleep_seconds(low: float, high: float) -> None:
    if high <= 0:
        return
    if low < 0:
        low = 0
    if high < low:
        low, high = high, low
    time.sleep(random.uniform(low, high))


def main() -> None:
    parser = argparse.ArgumentParser(description="Rehydrate Jekyll posts from source_url into a new output directory.")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--file", type=str, help="Single _posts markdown file to rehydrate.")
    group.add_argument("--dir", type=str, default=str(DEFAULT_POSTS_DIR), help="Directory containing _posts markdown files.")
    parser.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR), help="Output directory for rehydrated posts.")
    parser.add_argument("--skipped-log", type=str, default=str(DEFAULT_LOG_PATH), help="YAML log file for skipped entries.")
    parser.add_argument("--between-min", type=float, default=2.0, help="Min seconds to sleep between articles.")
    parser.add_argument("--between-max", type=float, default=6.0, help="Max seconds to sleep between articles.")
    parser.add_argument("--batch-min", type=int, default=3, help="Min articles per batch before long sleep.")
    parser.add_argument("--batch-max", type=int, default=5, help="Max articles per batch before long sleep.")
    parser.add_argument("--sleep-min", type=float, default=180.0, help="Min seconds to long-sleep between batches.")
    parser.add_argument("--sleep-max", type=float, default=600.0, help="Max seconds to long-sleep between batches.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    skipped_log = Path(args.skipped_log)

    if args.file:
        post_files = [Path(args.file)]
    else:
        post_files = iter_post_files(Path(args.dir))

    if not post_files:
        print("No markdown posts found to rehydrate.", file=sys.stderr)
        return

    batch_target = random.randint(max(1, args.batch_min), max(1, args.batch_max))
    processed_in_batch = 0

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fetch_article import fetch_article

    for idx, post_path in enumerate(post_files, 1):
        try:
            fm = read_front_matter(post_path)
        except Exception as e:
            _append_skipped(skipped_log, {"path": str(post_path), "reason": f"front_matter_error: {e}"})
            continue

        print(f"[{idx}/{len(post_files)}] Fetching: {fm.source_url[:80]}...")
        try:
            article = fetch_article(fm.source_url)
            if not (article.get("title") and article.get("body_md")):
                raise ValueError("Empty title/body after fetch.")
            out_path = write_rehydrated_post(
                out_dir=out_dir,
                original_filename=post_path.name,
                article=article,
                categories=fm.categories,
                source_url=fm.source_url,
            )
            print(f"  -> Wrote: {out_path}")
        except Exception as e:
            print(f"  -> Skipped: {e}", file=sys.stderr)
            _append_skipped(
                skipped_log,
                {
                    "path": str(post_path),
                    "source_url": fm.source_url,
                    "reason": f"fetch_error: {e}",
                },
            )
            continue

        processed_in_batch += 1
        _sleep_seconds(args.between_min, args.between_max)

        if processed_in_batch >= batch_target:
            print(f"Batch reached ({processed_in_batch}); sleeping long to avoid WeChat throttling...")
            _sleep_seconds(args.sleep_min, args.sleep_max)
            processed_in_batch = 0
            batch_target = random.randint(max(1, args.batch_min), max(1, args.batch_max))


if __name__ == "__main__":
    main()

