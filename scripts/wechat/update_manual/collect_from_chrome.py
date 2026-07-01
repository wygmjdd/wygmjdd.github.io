"""Collect new WeChat article URLs from Chrome history for update_manual batches."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.wechat.wechat_url_stub import canonical_source_url

_UPDATE_MANUAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = _UPDATE_MANUAL_DIR.parents[2]
DOCS_DIR = REPO_ROOT / "content" / "docs"
INPUT_DIR = _UPDATE_MANUAL_DIR / "input"

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


def is_wechat_article_url(url: str) -> bool:
    return bool(WECHAT_ARTICLE_RE.match(normalize_collect_url(url)))


def is_collectable_wechat_url(url: str) -> bool:
    canon = normalize_collect_url(url)
    if not is_wechat_article_url(canon):
        return False
    if "tempkey=" in canon.lower():
        return False
    return True


def load_existing_source_urls(docs_dir: Path) -> set[str]:
    existing: set[str] = set()
    if not docs_dir.is_dir():
        return existing
    for path in docs_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("---", 3)
        if end < 0:
            continue
        for line in text[3:end].splitlines():
            stripped = line.strip()
            if stripped.startswith("source_url:"):
                val = stripped.split(":", 1)[1].strip().strip('"\'')
                if val:
                    existing.add(normalize_collect_url(val))
                break
    return existing


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
) -> list[CollectedArticle]:
    seen: set[str] = set()
    articles: list[CollectedArticle] = []
    for article in query_wechat_articles(history_path, days=days, biz=biz):
        if article.url in seen or article.url in existing:
            continue
        seen.add(article.url)
        articles.append(article)
    return articles


def batch_entry(article: CollectedArticle, *, slug: str) -> dict[str, str]:
    entry = {
        "title": article.title,
        "slug": slug,
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
        help="Category slug for every collected URL (default: di-tie-ri-ji).",
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

    history_path = Path(args.history_path).expanduser() if args.history_path else chrome_history_path(
        args.channel,
        args.profile,
    )
    existing = load_existing_source_urls(DOCS_DIR)
    biz = args.biz.strip() or None

    print(f"Chrome history: {history_path}", flush=True)
    print(f"Lookback      : {args.days} day(s)", flush=True)
    print(f"Slug          : {args.default_slug}", flush=True)
    print(f"Already in site: {len(existing)} source_url(s) in {DOCS_DIR}", flush=True)

    try:
        new_articles = collect_new_articles(
            history_path,
            days=args.days,
            biz=biz,
            existing=existing,
        )
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if not new_articles:
        print("No new WeChat article URLs found in Chrome history.", flush=True)
        return

    print(f"New URLs      : {len(new_articles)}", flush=True)
    for article in new_articles:
        title_part = f"{article.title} — " if article.title else ""
        print(f"  {title_part}{article.url}", flush=True)

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
        print("Review titles and edit slug per entry if needed, then run:", flush=True)
        print(f"  python3 -m scripts.wechat.update_manual {args.batch_id}", flush=True)


if __name__ == "__main__":
    main()
