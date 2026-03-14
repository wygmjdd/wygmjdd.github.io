"""
Migration pipeline: read wechat_albums.yml, get article URLs per album (parse or manual),
dedupe, fetch each article, write _posts with categories. Supports --dry-run and --resume.
"""

import argparse
import re
import sys
from pathlib import Path

# Allow importing other scripts when run from repo root (e.g. python scripts/migrate.py)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml

# Run from repo root or scripts/; repo root = parent of scripts/ or cwd
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "_data"
POSTS_DIR = REPO_ROOT / "_posts"
DONE_FILE = REPO_ROOT / "scripts" / ".migrate_done"


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


def get_article_urls_per_album(albums: list[dict], manual_urls: dict, use_playwright: bool) -> dict[str, list[str]]:
    """Return album_slug -> list of article URLs. Uses parse_album or manual_urls when available."""
    from slug_from_album import slug_from_album

    result: dict[str, list[str]] = {}
    for album in albums:
        name = album.get("name", "")
        slug = slug_from_album(name, album.get("slug"))
        url = album.get("url", "")
        if manual_urls and slug in manual_urls:
            result[slug] = list(manual_urls[slug])
            continue
        if use_playwright and url:
            try:
                from parse_album import parse_album
                result[slug] = parse_album(url)
            except Exception as e:
                print(f"Warning: parse_album failed for {slug}: {e}", file=sys.stderr)
                result[slug] = []
        else:
            result[slug] = []
    return result


def build_url_to_slugs(album_urls: dict[str, list[str]]) -> dict[str, list[str]]:
    url_to_slugs: dict[str, list[str]] = {}
    for slug, urls in album_urls.items():
        for u in urls:
            u = u.strip().split("#")[0]
            if not u:
                continue
            if u not in url_to_slugs:
                url_to_slugs[u] = []
            if slug not in url_to_slugs[u]:
                url_to_slugs[u].append(slug)
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
                        urls.add(val)
                        break
    return urls


def load_done_urls() -> set[str]:
    if not DONE_FILE.exists():
        return set()
    return set(DONE_FILE.read_text(encoding="utf-8").strip().splitlines())


def append_done_url(url: str) -> None:
    DONE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DONE_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


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
        print(f"[dry-run] Would write {path.name}")
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
    parser.add_argument("--no-playwright", action="store_true", help="Do not use Playwright; only use manual URL list")
    args = parser.parse_args()

    albums = load_albums_config()
    manual_urls = load_manual_urls()
    album_urls = get_article_urls_per_album(albums, manual_urls, use_playwright=not args.no_playwright)
    url_to_slugs = build_url_to_slugs(album_urls)

    done = set()
    if args.resume:
        done = existing_source_urls() | load_done_urls()

    from fetch_article import fetch_article
    total = len(url_to_slugs)
    for i, (url, slugs) in enumerate(url_to_slugs.items(), 1):
        if url in done:
            continue
        print(f"[{i}/{total}] Fetching: {url[:60]}...")
        try:
            article = fetch_article(url)
            write_post(article, slugs, dry_run=args.dry_run)
            if not args.dry_run:
                append_done_url(url)
            done.add(url)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
        if not args.dry_run and i < total:
            import time
            time.sleep(3)

    if not args.dry_run and url_to_slugs:
        update_categories_yml(albums)


if __name__ == "__main__":
    main()
