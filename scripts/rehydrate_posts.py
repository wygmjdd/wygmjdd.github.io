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


def _canonical_source_url(url: str) -> str:
    return html.unescape(url.strip()).split("#")[0]


def _resolve_repo_path(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = REPO_ROOT / p
    return p.resolve()


def post_paths_from_skipped_log(log_path: Path) -> list[Path]:
    """Load skipped YAML; dedupe by canonical source_url; return existing _posts paths."""
    if not log_path.is_file():
        print(f"Skipped log not found: {log_path}", file=sys.stderr)
        return []
    raw = yaml.safe_load(log_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        return []
    seen: set[str] = set()
    paths: list[Path] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        p_raw = entry.get("path")
        u_raw = entry.get("source_url")
        if not isinstance(p_raw, str) or not isinstance(u_raw, str):
            continue
        key = _canonical_source_url(u_raw)
        if key in seen:
            continue
        seen.add(key)
        candidate = _resolve_repo_path(p_raw)
        if candidate.is_file():
            paths.append(candidate)
        else:
            print(f"Warning: skip log path missing, dropped: {candidate}", file=sys.stderr, flush=True)
    return sorted(paths, key=lambda x: x.name)


def dedupe_skipped_log_on_disk(log_path: Path) -> int:
    """Rewrite skipped log: one entry per canonical source_url (keeps longest reason). Returns new count."""
    if not log_path.is_file():
        return 0
    raw = yaml.safe_load(log_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        return 0
    merged: dict[str, dict] = {}
    order: list[str] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        u_raw = entry.get("source_url")
        p_raw = entry.get("path")
        if not isinstance(u_raw, str) or not isinstance(p_raw, str):
            continue
        key = _canonical_source_url(u_raw)
        reason = entry.get("reason", "")
        reason_s = str(reason) if reason is not None else ""
        try:
            rel = _resolve_repo_path(p_raw).relative_to(REPO_ROOT)
            path_out = str(rel).replace("\\", "/")
        except ValueError:
            path_out = str(_resolve_repo_path(p_raw))
        if key not in merged:
            order.append(key)
            merged[key] = {
                "path": path_out,
                "source_url": key,
                "reason": reason_s,
            }
        else:
            prev = str(merged[key].get("reason") or "")
            if len(reason_s) > len(prev):
                merged[key]["reason"] = reason_s
    out_list = [merged[k] for k in order]
    log_path.write_text(
        yaml.dump(out_list, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    return len(out_list)


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
    parser = argparse.ArgumentParser(
        description="Rehydrate Jekyll posts from source_url into a new output directory.",
        epilog="Example (test 2 stubs): python scripts/rehydrate_posts.py --file a.md --file b.md",
    )
    parser.add_argument(
        "--file",
        action="append",
        dest="files",
        metavar="PATH",
        default=None,
        help="Path to one _posts markdown; repeat --file for multiple (e.g. smoke-test two articles).",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=str(DEFAULT_POSTS_DIR),
        help="Directory containing _posts markdown files (ignored if --file or --from-skipped-log).",
    )
    parser.add_argument(
        "--from-skipped-log",
        type=str,
        default=None,
        metavar="PATH",
        help="Retry only posts in a skipped YAML log, deduped by canonical source_url (e.g. scripts/rehydrate_skipped.yml).",
    )
    parser.add_argument(
        "--dedupe-skipped-log-only",
        type=str,
        default=None,
        metavar="PATH",
        help="Rewrite the given skipped log in place (dedupe by URL); then exit without fetching.",
    )
    parser.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR), help="Output directory for rehydrated posts.")
    parser.add_argument("--skipped-log", type=str, default=str(DEFAULT_LOG_PATH), help="YAML log file for skipped entries.")
    parser.add_argument("--between-min", type=float, default=2.0, help="Min seconds to sleep between articles.")
    parser.add_argument("--between-max", type=float, default=6.0, help="Max seconds to sleep between articles.")
    parser.add_argument("--batch-min", type=int, default=3, help="Min articles per batch before long sleep.")
    parser.add_argument("--batch-max", type=int, default=5, help="Max articles per batch before long sleep.")
    parser.add_argument("--sleep-min", type=float, default=180.0, help="Min seconds to long-sleep between batches.")
    parser.add_argument("--sleep-max", type=float, default=600.0, help="Max seconds to long-sleep between batches.")
    args = parser.parse_args()

    if args.dedupe_skipped_log_only:
        log_p = Path(args.dedupe_skipped_log_only)
        if not log_p.is_absolute():
            log_p = REPO_ROOT / log_p
        n = dedupe_skipped_log_on_disk(log_p)
        print(f"Deduped skipped log → {n} entr(y/ies): {log_p}", flush=True)
        return

    out_dir = Path(args.out_dir)
    skipped_log = Path(args.skipped_log)

    if args.from_skipped_log:
        log_p = Path(args.from_skipped_log)
        if not log_p.is_absolute():
            log_p = REPO_ROOT / log_p
        post_files = post_paths_from_skipped_log(log_p)
        posts_dir = f"from-skipped-log ({log_p.name})"
    elif args.files:
        post_files = [Path(f) for f in args.files]
        posts_dir = (
            post_files[0].parent
            if len(post_files) == 1
            else f"{len(post_files)} explicit --file path(s)"
        )
    else:
        post_files = iter_post_files(Path(args.dir))
        posts_dir = Path(args.dir)

    if not post_files:
        print("No markdown posts found to rehydrate.", file=sys.stderr)
        return
    print("=" * 64, flush=True)
    print("rehydrate_posts.py — _posts → _rehydrated_posts", flush=True)
    print(f"  input : {posts_dir}", flush=True)
    print(f"  output: {out_dir}", flush=True)
    print(f"  files : {len(post_files)} markdown file(s)", flush=True)
    print("=" * 64, flush=True)

    batch_target = random.randint(max(1, args.batch_min), max(1, args.batch_max))
    processed_in_batch = 0

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fetch_article import fetch_article

    for idx, post_path in enumerate(post_files, 1):
        try:
            fm = read_front_matter(post_path)
        except Exception as e:
            print(f"[{idx}/{len(post_files)}] SKIP {post_path.name} — bad front matter: {e}", flush=True)
            _append_skipped(skipped_log, {"path": str(post_path), "reason": f"front_matter_error: {e}"})
            continue

        print(f"[{idx}/{len(post_files)}] {post_path.name}", flush=True)
        print(f"    source: {fm.source_url[:88]}…" if len(fm.source_url) > 88 else f"    source: {fm.source_url}", flush=True)
        if fm.categories:
            print(f"    categories: {', '.join(fm.categories)}", flush=True)
        print("    fetching HTML → markdown + local images (please wait)…", flush=True)
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
            title_preview = (article.get("title") or "")[:60]
            print(f"    OK → {out_path.name} — «{title_preview}»", flush=True)
        except Exception as e:
            print(f"    SKIP: {e}", file=sys.stderr, flush=True)
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
        print(
            f"    pause {args.between_min:.1f}–{args.between_max:.1f}s before next post…",
            flush=True,
        )
        _sleep_seconds(args.between_min, args.between_max)

        if processed_in_batch >= batch_target:
            print(
                f"Batch limit ({processed_in_batch} posts); long sleep "
                f"{args.sleep_min:.0f}–{args.sleep_max:.0f}s (anti-throttle)…",
                flush=True,
            )
            _sleep_seconds(args.sleep_min, args.sleep_max)
            processed_in_batch = 0
            batch_target = random.randint(max(1, args.batch_min), max(1, args.batch_max))

    print("=" * 64, flush=True)
    print(f"Finished processing {len(post_files)} file(s). Skipped log: {skipped_log}", flush=True)


if __name__ == "__main__":
    main()

