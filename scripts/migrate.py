"""
Migration pipeline: read wechat_albums.yml, get article URLs per album (parse or manual),
dedupe, fetch each article, write _posts with categories. Supports --dry-run and --resume.

Stub mode (--stubs-only): one file per unique article URL; filename is stable from URL hash
so rehydrate/Hugo steps stay aligned. Multi-album membership is merged into `categories`.
Do not mix full migrate and stubs-only for the same URLs (would create duplicate files).
"""

import argparse
import hashlib
import html
import re
import sys
from pathlib import Path

# Allow importing other scripts when run from repo root (e.g. python scripts/migrate.py)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml

# Run from repo root or scripts/; repo root = parent of scripts/ or cwd
REPO_ROOT = Path(__file__).resolve().parent.parent
LEGACY_JEKYLL = REPO_ROOT / "_archive" / "legacy-jekyll"
DATA_DIR = LEGACY_JEKYLL / "_data"
POSTS_DIR = LEGACY_JEKYLL / "_posts"
DONE_FILE = REPO_ROOT / "scripts" / ".migrate_done"

# Placeholder date in stub front matter + filename; real date comes from rehydrate fetch.
STUB_DATE = "2033-01-01"
STUB_HASH_LEN = 10


def canonical_source_url(url: str) -> str:
    u = html.unescape(url.strip())
    return u.split("#")[0]


def load_albums_config() -> list[dict]:
    config_path = DATA_DIR / "wechat_albums.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("albums", [])


def load_manual_urls() -> dict[str, list[str]]:
    for path in (DATA_DIR / "wechat_manual_article_urls.yml", REPO_ROOT / "scripts" / "manual_article_urls.yml"):
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    return {}


def get_article_urls_per_album(
    albums: list[dict],
    manual_urls: dict,
    use_playwright: bool,
    *,
    verbose: bool = True,
) -> dict[str, list[str]]:
    """Return album_slug -> list of article URLs. Uses parse_album or manual_urls when available."""
    from slug_from_album import slug_from_album

    def _log(msg: str) -> None:
        if verbose:
            print(msg, flush=True)

    n_albums = len(albums)
    result: dict[str, list[str]] = {}
    for idx, album in enumerate(albums, 1):
        name = album.get("name", "")
        slug = slug_from_album(name, album.get("slug"))
        url = album.get("url", "")
        _log(f"[album {idx}/{n_albums}] {slug} — {name or '(no name)'}")
        if manual_urls and slug in manual_urls:
            result[slug] = list(manual_urls[slug])
            _log(f"    using manual URL list ({len(result[slug])} articles)")
            continue
        if use_playwright and url:
            try:
                from parse_album import parse_album
                result[slug] = parse_album(url, verbose=verbose)
            except Exception as e:
                print(f"    ERROR parse_album: {e}", file=sys.stderr, flush=True)
                result[slug] = []
        elif not url:
            result[slug] = []
            _log("    skipped (no album url in wechat_albums.yml)")
        else:
            result[slug] = []
            _log("    skipped (--no-playwright and no manual list for this album)")
    return result


def build_url_to_slugs(album_urls: dict[str, list[str]]) -> dict[str, list[str]]:
    url_to_slugs: dict[str, list[str]] = {}
    for slug, urls in album_urls.items():
        for u in urls:
            u_clean = canonical_source_url(u)
            if not u_clean:
                continue
            if u_clean not in url_to_slugs:
                url_to_slugs[u_clean] = []
            if slug not in url_to_slugs[u_clean]:
                url_to_slugs[u_clean].append(slug)
    return url_to_slugs


def slugify_title(title: str, max_len: int = 40) -> str:
    from pypinyin import lazy_pinyin
    if not title:
        return "post"
    if all(ord(c) < 128 for c in title):
        s = re.sub(r"[^\w\s-]", "", title).strip().lower()
        s = re.sub(r"[-\s]+", "-", s)
    else:
        s = "".join(lazy_pinyin(title)).lower()
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:max_len] or "post"


def existing_source_urls() -> set[str]:
    urls = set()
    if not POSTS_DIR.exists():
        return urls
    for p in POSTS_DIR.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end > 0:
                fm = text[3:end]
                for line in fm.splitlines():
                    if line.strip().startswith("source_url:"):
                        val = line.split(":", 1)[1].strip().strip('"\'')
                        urls.add(canonical_source_url(val))
                        break
    return urls


def load_done_urls() -> set[str]:
    if not DONE_FILE.exists():
        return set()
    lines = [x.strip() for x in DONE_FILE.read_text(encoding="utf-8").splitlines() if x.strip()]
    return {canonical_source_url(x) for x in lines}


def append_done_url(url: str) -> None:
    DONE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DONE_FILE, "a", encoding="utf-8") as f:
        f.write(canonical_source_url(url) + "\n")


def stub_filename_for_url(url: str) -> str:
    key = hashlib.sha256(canonical_source_url(url).encode("utf-8")).hexdigest()[:STUB_HASH_LEN]
    return f"{STUB_DATE}-post-{key}.md"


def _read_post_front_matter_raw(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end < 0:
        return None
    return text[3:end]


def write_or_merge_stub(url: str, categories: list[str], dry_run: bool) -> Path | None:
    """Create or update a stub post; merges category slugs when the stub already exists."""
    canonical = canonical_source_url(url)
    merged_cats = sorted({c.strip() for c in categories if c and str(c).strip()})
    name = stub_filename_for_url(canonical)
    path = POSTS_DIR / name
    if dry_run:
        action = "update" if path.exists() else "create"
        print(f"[dry-run] Would {action} stub {name} categories={merged_cats}", flush=True)
        return path

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        fm_raw = _read_post_front_matter_raw(path)
        if not fm_raw:
            print(f"Warning: skip merge, invalid front matter: {path}", file=sys.stderr)
            return path
        data = yaml.safe_load(fm_raw) or {}
        if not isinstance(data, dict):
            return path
        existing = data.get("categories") or []
        if isinstance(existing, str):
            existing = [existing]
        elif not isinstance(existing, list):
            existing = []
        prev = {str(x).strip() for x in existing if str(x).strip()}
        prev.update(merged_cats)
        combined = sorted(prev)
        if data.get("categories") == combined and canonical_source_url(
            str(data.get("source_url") or "")
        ) == canonical:
            return path
        data["categories"] = combined
        data["source_url"] = canonical
        data.setdefault("title", "")
        data["date"] = STUB_DATE
        fm_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        path.write_text(f"---\n{fm_str}---\n\n", encoding="utf-8")
        print(f"  merged stub {name} -> categories={combined}", flush=True)
        return path

    front_matter = {
        "title": "",
        "date": STUB_DATE,
        "categories": merged_cats,
        "source_url": canonical,
    }
    fm_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{fm_str}---\n\n", encoding="utf-8")
    print(f"  wrote stub {name}", flush=True)
    return path


def write_post(article: dict, categories: list[str], dry_run: bool) -> Path | None:
    date_str = article["date"] if isinstance(article["date"], str) else article["date"].strftime("%Y-%m-%d")
    title_slug = slugify_title(article["title"])
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    base = f"{date_str}-{title_slug}.md"
    path = POSTS_DIR / base
    n = 1
    while path.exists():
        n += 1
        path = POSTS_DIR / f"{date_str}-{title_slug}-{n}.md"
    if dry_run:
        print(f"[dry-run] Would write {path.name}", flush=True)
        return path
    front_matter = {
        "title": article["title"],
        "date": date_str,
        "categories": categories,
        "source_url": article["source_url"],
    }
    fm_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    body = article["body_md"]
    path.write_text(f"---\n{fm_str}---\n\n{body}\n", encoding="utf-8")
    return path


def update_categories_yml(albums: list[dict]) -> None:
    from slug_from_album import slug_from_album
    path = DATA_DIR / "categories.yml"
    existing = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                existing = data
    for album in albums:
        slug = slug_from_album(album.get("name", ""), album.get("slug"))
        existing[slug] = album.get("name", slug)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(existing, f, allow_unicode=True, default_flow_style=False, sort_keys=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate WeChat articles from albums to Jekyll _posts")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files")
    parser.add_argument("--resume", action="store_true", help="Skip URLs already in _posts or .migrate_done")
    parser.add_argument(
        "--no-playwright",
        action="store_true",
        help="Do not use Playwright; only use manual URL list",
    )
    parser.add_argument(
        "--stubs-only",
        action="store_true",
        help="Only write placeholder _posts (source_url + categories); no fetch. Filenames: "
        f"{STUB_DATE}-post-<{STUB_HASH_LEN}-char hash>.md",
    )
    args = parser.parse_args()

    mode_label = "stubs-only (no article fetch)" if args.stubs_only else "full fetch → _posts"
    print("=" * 64, flush=True)
    print("migrate.py — WeChat albums → Jekyll _posts", flush=True)
    print(f"  config : {DATA_DIR / 'wechat_albums.yml'}", flush=True)
    print(f"  _posts : {POSTS_DIR}", flush=True)
    print(f"  mode   : {mode_label}{' [DRY-RUN]' if args.dry_run else ''}", flush=True)
    if args.resume and not args.stubs_only:
        print("  resume : skip URLs already in _posts or scripts/.migrate_done", flush=True)
    if args.no_playwright:
        print("  note   : --no-playwright (album pages need manual URL YAML or will be empty)", flush=True)
    print("=" * 64, flush=True)

    albums = load_albums_config()
    print(f"Loaded {len(albums)} album(s) from config.", flush=True)
    manual_urls = load_manual_urls()
    if manual_urls:
        print(f"Manual URL overrides loaded for {len(manual_urls)} album slug(s).", flush=True)

    album_urls = get_article_urls_per_album(
        albums,
        manual_urls,
        use_playwright=not args.no_playwright,
        verbose=True,
    )
    url_to_slugs = build_url_to_slugs(album_urls)
    raw_link_total = sum(len(v) for v in album_urls.values())
    print("-" * 64, flush=True)
    print(
        f"Album phase done: {raw_link_total} link row(s) across albums → "
        f"{len(url_to_slugs)} unique article URL(s) after dedupe.",
        flush=True,
    )
    print("-" * 64, flush=True)

    if args.stubs_only:
        total = len(url_to_slugs)
        print(f"Writing stubs for {total} unique URL(s)…", flush=True)
        for i, (url, slugs) in enumerate(url_to_slugs.items(), 1):
            print(f"[stub {i}/{total}] {canonical_source_url(url)[:76]}…", flush=True)
            print(f"    categories: {', '.join(slugs)}", flush=True)
            try:
                write_or_merge_stub(url, slugs, dry_run=args.dry_run)
            except Exception as e:
                print(f"    ERROR: {e}", file=sys.stderr, flush=True)
        if not args.dry_run and url_to_slugs:
            update_categories_yml(albums)
            print(f"Updated {DATA_DIR / 'categories.yml'}.", flush=True)
        print("=" * 64, flush=True)
        print(f"Done. {total} stub(s) processed.", flush=True)
        return

    done: set[str] = set()
    if args.resume:
        done = existing_source_urls() | load_done_urls()
        print(
            f"Resume: {len(done)} URL(s) already recorded; will skip those.",
            flush=True,
        )

    from fetch_article import fetch_article

    pending = [(u, s) for u, s in url_to_slugs.items() if u not in done]
    n_total = len(url_to_slugs)
    n_pending = len(pending)
    print(
        f"Fetch queue: {n_pending} to download (of {n_total} unique URLs).",
        flush=True,
    )
    if n_pending == 0:
        print("Nothing to fetch. Done.", flush=True)
        if not args.dry_run and url_to_slugs:
            update_categories_yml(albums)
        return

    import time as time_module

    for j, (url, slugs) in enumerate(pending, 1):
        print(f"[fetch {j}/{n_pending}] {canonical_source_url(url)[:76]}…", flush=True)
        print(f"    categories: {', '.join(slugs)}", flush=True)
        try:
            article = fetch_article(url)
            out_path = write_post(article, slugs, dry_run=args.dry_run)
            if out_path:
                print(f"    wrote: {out_path.name}", flush=True)
            if not args.dry_run:
                append_done_url(url)
            done.add(url)
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr, flush=True)
        if not args.dry_run and j < n_pending:
            print("    sleeping 3s before next article…", flush=True)
            time_module.sleep(3)

    if not args.dry_run and url_to_slugs:
        update_categories_yml(albums)
        print(f"Updated {DATA_DIR / 'categories.yml'}.", flush=True)
    print("=" * 64, flush=True)
    print(f"Done. Fetched {n_pending} article(s).", flush=True)


if __name__ == "__main__":
    main()
