"""Collect new WeChat article URLs from Chrome history for update_manual batches."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from scripts.wechat.article_metadata import (
    ArticlePageMetadata,
    extract_article_key_from_url,
    fetch_article_metadata,
)
from scripts.wechat.wechat_url_stub import canonical_source_url

_UPDATE_MANUAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = _UPDATE_MANUAL_DIR.parents[2]
DOCS_DIR = REPO_ROOT / "content" / "docs"
INPUT_DIR = _UPDATE_MANUAL_DIR / "input"
CATEGORIES_YML = REPO_ROOT / "data" / "categories.yml"
ARTICLE_KEYS_YML = REPO_ROOT / "data" / "wechat_article_keys.yml"

CHROME_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)

CHANNEL_DIRS: dict[str, str] = {
    "stable": "Chrome",
    "beta": "Chrome Beta",
    "canary": "Chrome Canary",
}

WECHAT_ARTICLE_RE = re.compile(
    r"^https?://[^/]*mp\.weixin\.qq\.com/s(?:/|\?)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CollectedArticle:
    url: str
    title: str
    visited_at: datetime
    category_title: str | None = None
    category_slug: str | None = None
    article_key: str | None = None


def chrome_history_path(channel: str, profile: str) -> Path:
    if channel not in CHANNEL_DIRS:
        raise ValueError(f"unsupported channel {channel!r}; choose from {sorted(CHANNEL_DIRS)}")
    home = Path.home()
    return home / "Library/Application Support/Google" / CHANNEL_DIRS[channel] / profile / "History"


def chrome_cutoff_timestamp(days: int) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    delta = cutoff - CHROME_EPOCH
    return int(delta.total_seconds() * 1_000_000)


def normalize_collect_url(url: str) -> str:
    canon = canonical_source_url(url)
    if canon.startswith("http://mp.weixin.qq.com"):
        canon = "https://" + canon[len("http://") :]
    return canon


def normalize_history_title(title: str | None) -> str:
    if not title:
        return ""
    cleaned = " ".join(str(title).split())
    return cleaned


def normalize_category_title(title: str) -> str:
    return "".join(str(title).split()).casefold()


def load_category_title_slugs(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    if not isinstance(data, list):
        return result
    for row in data:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "").strip()
        slug = str(row.get("slug") or "").strip()
        if title and slug:
            result[normalize_category_title(title)] = slug
    return result


def detect_article_category(
    article: CollectedArticle,
    category_title_slugs: dict[str, str],
    *,
    fetch_metadata: Callable[[str], ArticlePageMetadata] = fetch_article_metadata,
    include_category: bool = True,
) -> CollectedArticle:
    if not include_category and article.article_key:
        return replace(article, category_title=None, category_slug=None)

    metadata = fetch_metadata(article.url)
    category_title = metadata.album_title if include_category else None
    category_slug = (
        category_title_slugs.get(normalize_category_title(category_title))
        if category_title
        else None
    )
    return replace(
        article,
        category_title=category_title,
        category_slug=category_slug,
        article_key=article.article_key or metadata.article_key,
    )


def is_wechat_article_url(url: str) -> bool:
    return bool(WECHAT_ARTICLE_RE.match(normalize_collect_url(url)))


def is_collectable_wechat_url(url: str) -> bool:
    canon = normalize_collect_url(url)
    if not is_wechat_article_url(canon):
        return False
    if "tempkey=" in canon.lower():
        return False
    return True


def _load_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}
    data = yaml.safe_load("\n".join(lines[1:end]))
    return data if isinstance(data, dict) else {}


def load_existing_source_urls(docs_dir: Path) -> set[str]:
    existing: set[str] = set()
    if not docs_dir.is_dir():
        return existing
    for path in docs_dir.rglob("*.md"):
        source_url = _load_front_matter(path).get("source_url")
        if isinstance(source_url, str) and source_url.strip():
            existing.add(normalize_collect_url(source_url))
    return existing


def article_keys_from_urls(urls: Iterable[str]) -> set[str]:
    return {
        key
        for url in urls
        if (key := extract_article_key_from_url(url))
    }


def load_article_key_cache(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}

    cache: dict[str, str] = {}
    for raw_url, raw_key in data.items():
        url = normalize_collect_url(str(raw_url))
        key = str(raw_key).strip()
        if url and key.count("|") == 3 and all(part.strip() for part in key.split("|")):
            cache[url] = key
    return cache


def update_article_key_cache(path: Path, articles: Iterable[CollectedArticle]) -> int:
    cache = load_article_key_cache(path)
    changed = 0
    for article in articles:
        if not article.article_key or extract_article_key_from_url(article.url):
            continue
        url = normalize_collect_url(article.url)
        if cache.get(url) == article.article_key:
            continue
        cache[url] = article.article_key
        changed += 1

    if changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(cache, allow_unicode=True, sort_keys=True),
            encoding="utf-8",
        )
    return changed


def load_existing_article_keys(
    docs_dir: Path,
    *,
    cache_path: Path = ARTICLE_KEYS_YML,
    article_key_cache: dict[str, str] | None = None,
    source_urls: set[str] | None = None,
) -> set[str]:
    if source_urls is None:
        source_urls = load_existing_source_urls(docs_dir)
    keys = article_keys_from_urls(source_urls)
    cache = (
        article_key_cache
        if article_key_cache is not None
        else load_article_key_cache(cache_path)
    )
    keys.update(cache[url] for url in source_urls if url in cache)
    return keys


def query_wechat_articles(history_path: Path, *, days: int, biz: str | None) -> list[CollectedArticle]:
    if not history_path.is_file():
        raise FileNotFoundError(f"Chrome history not found: {history_path}")

    cutoff_ts = chrome_cutoff_timestamp(days)
    rows: list[tuple[str, str | None, int]] = []

    with tempfile.TemporaryDirectory() as tmp:
        copy_path = Path(tmp) / "History"
        shutil.copy2(history_path, copy_path)
        conn = sqlite3.connect(f"file:{copy_path}?mode=ro", uri=True)
        try:
            cursor = conn.execute(
                """
                SELECT u.url, u.title, MAX(v.visit_time) AS last_visit
                FROM urls u
                INNER JOIN visits v ON u.id = v.url
                WHERE v.visit_time >= ?
                GROUP BY u.id
                ORDER BY last_visit DESC
                """,
                (cutoff_ts,),
            )
            rows = [(url, title, last_visit) for url, title, last_visit in cursor.fetchall()]
        finally:
            conn.close()

    results: list[CollectedArticle] = []
    biz_needle = biz.strip() if biz else None
    for url, title, last_visit in rows:
        if not is_collectable_wechat_url(url):
            continue
        canon = normalize_collect_url(url)
        if biz_needle and biz_needle not in canon:
            is_short_link = bool(re.search(r"mp\.weixin\.qq\.com/s/[^/?]+$", canon, re.I))
            if not is_short_link:
                continue
        visited_at = CHROME_EPOCH + timedelta(microseconds=last_visit)
        results.append(
            CollectedArticle(
                url=canon,
                title=normalize_history_title(title),
                visited_at=visited_at,
            )
        )
    return results


def collect_new_articles(
    history_path: Path,
    *,
    days: int,
    biz: str | None,
    existing: set[str],
    existing_keys: set[str] | None = None,
    article_key_cache: dict[str, str] | None = None,
) -> list[CollectedArticle]:
    known_keys = existing_keys or set()
    cached_keys = article_key_cache or {}
    seen: set[str] = set()
    seen_keys: set[str] = set()
    articles: list[CollectedArticle] = []
    for article in query_wechat_articles(history_path, days=days, biz=biz):
        article_key = (
            extract_article_key_from_url(article.url)
            or cached_keys.get(article.url)
        )
        if article.url in seen or article.url in existing:
            continue
        if article_key and (article_key in known_keys or article_key in seen_keys):
            continue
        seen.add(article.url)
        if article_key:
            seen_keys.add(article_key)
            article = replace(article, article_key=article_key)
        articles.append(article)
    return articles


def deduplicate_detected_articles(
    articles: list[CollectedArticle],
    *,
    existing_keys: set[str],
) -> tuple[list[CollectedArticle], list[CollectedArticle]]:
    kept: list[CollectedArticle] = []
    skipped: list[CollectedArticle] = []
    seen_keys: set[str] = set()
    for article in articles:
        key = article.article_key
        if key and (key in existing_keys or key in seen_keys):
            skipped.append(article)
            continue
        if key:
            seen_keys.add(key)
        kept.append(article)
    return kept, skipped


def batch_entry(article: CollectedArticle, *, slug: str) -> dict[str, str]:
    entry = {
        "title": article.title,
        "slug": article.category_slug or slug,
        "url": article.url,
    }
    return entry


def write_batch_json(
    batch_id: str,
    articles: list[CollectedArticle],
    *,
    slug: str,
    dry_run: bool,
) -> Path:
    payload = [batch_entry(article, slug=slug) for article in articles]
    out_path = INPUT_DIR / f"{batch_id}.json"
    if dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2), flush=True)
        return out_path

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Read Chrome history for mp.weixin.qq.com/s URLs not yet in content/docs, "
            "and write scripts/wechat/update_manual/input/<batch-id>.json."
        ),
    )
    parser.add_argument(
        "--batch-id",
        default=datetime.now().strftime("%Y-%m-%d"),
        metavar="YYYY-MM-DD",
        help="Output batch id (default: today).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Look back this many days in Chrome history (default: 1, today only).",
    )
    parser.add_argument(
        "--default-slug",
        default="di-tie-ri-ji",
        help="Fallback category slug when the WeChat collection cannot be detected.",
    )
    parser.add_argument(
        "--no-detect-category",
        action="store_true",
        help="Skip WeChat collection detection and use --default-slug for every article.",
    )
    parser.add_argument(
        "--channel",
        choices=sorted(CHANNEL_DIRS),
        default="beta",
        help="Chrome channel (default: beta).",
    )
    parser.add_argument(
        "--profile",
        default="Default",
        help='Chrome profile directory name (default: "Default").',
    )
    parser.add_argument(
        "--history-path",
        type=str,
        default="",
        help="Override path to Chrome History SQLite file.",
    )
    parser.add_argument(
        "--biz",
        type=str,
        default="",
        help="Optional __biz= filter for long WeChat URLs (short /s/ links are kept).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print JSON to stdout instead of writing the batch file.",
    )
    args = parser.parse_args()

    if args.days < 1:
        print("ERROR: --days must be >= 1", file=sys.stderr)
        raise SystemExit(2)

    history_path = (
        Path(args.history_path).expanduser()
        if args.history_path
        else chrome_history_path(
            args.channel,
            args.profile,
        )
    )
    existing = load_existing_source_urls(DOCS_DIR)
    article_key_cache = load_article_key_cache(ARTICLE_KEYS_YML)
    existing_keys = load_existing_article_keys(
        DOCS_DIR,
        article_key_cache=article_key_cache,
        source_urls=existing,
    )
    category_title_slugs = load_category_title_slugs(CATEGORIES_YML)
    biz = args.biz.strip() or None

    print(f"Chrome history: {history_path}", flush=True)
    print(f"Lookback      : {args.days} day(s)", flush=True)
    print(f"Fallback slug : {args.default_slug}", flush=True)
    print(
        f"Auto category : {'off' if args.no_detect_category else 'on'}",
        flush=True,
    )
    print(f"Already in site: {len(existing)} source_url(s) in {DOCS_DIR}", flush=True)

    try:
        new_articles = collect_new_articles(
            history_path,
            days=args.days,
            biz=biz,
            existing=existing,
            existing_keys=existing_keys,
            article_key_cache=article_key_cache,
        )
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if not new_articles:
        print("No new WeChat article URLs found in Chrome history.", flush=True)
        return

    detected_articles: list[CollectedArticle] = []
    for article in new_articles:
        try:
            article = detect_article_category(
                article,
                category_title_slugs,
                include_category=not args.no_detect_category,
            )
        except Exception as exc:
            if not article.article_key:
                print(
                    f"[warn] article metadata lookup failed for {article.url}: {exc}; "
                    "skipping until a stable identity can be read",
                    file=sys.stderr,
                    flush=True,
                )
                continue
            print(
                f"[warn] article metadata lookup failed for {article.url}: {exc}; "
                f"using {args.default_slug!r}",
                file=sys.stderr,
                flush=True,
            )
        detected_articles.append(article)
    new_articles, skipped_articles = deduplicate_detected_articles(
        detected_articles,
        existing_keys=existing_keys,
    )
    if not args.dry_run:
        cached_count = update_article_key_cache(ARTICLE_KEYS_YML, detected_articles)
        if cached_count:
            print(
                f"Cached identity for {cached_count} short article URL(s) in "
                f"{ARTICLE_KEYS_YML.relative_to(REPO_ROOT)}.",
                flush=True,
            )
    for article in skipped_articles:
        print(
            f"[skip] already collected article identity: {article.title or article.url}",
            flush=True,
        )

    if not new_articles:
        print("No new WeChat articles remain after identity checks.", flush=True)
        return

    print(f"New URLs      : {len(new_articles)}", flush=True)
    for article in new_articles:
        title_part = f"{article.title} — " if article.title else ""
        if article.category_slug:
            category_part = f" [{article.category_title} -> {article.category_slug}]"
        elif article.category_title:
            category_part = (
                f" [unknown collection {article.category_title!r}; "
                f"fallback -> {args.default_slug}]"
            )
        else:
            category_part = f" [fallback -> {args.default_slug}]"
        print(f"  {title_part}{article.url}{category_part}", flush=True)

    out_path = write_batch_json(
        args.batch_id,
        new_articles,
        slug=args.default_slug,
        dry_run=args.dry_run,
    )
    if args.dry_run:
        print(f"(dry-run; would write {out_path.relative_to(REPO_ROOT)})", flush=True)
    else:
        print(f"Wrote {out_path.relative_to(REPO_ROOT)}", flush=True)
        print("Review titles and any fallback slug, then run:", flush=True)
        print(f"  python3 -m scripts.wechat.update_manual {args.batch_id}", flush=True)


if __name__ == "__main__":
    main()
