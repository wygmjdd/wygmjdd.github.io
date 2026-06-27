"""Merge ``input/<batch>.json`` into manual URL YAML, then publish to Hugo.

``migrate_jekyll_to_hugo_book.py`` wipes and rebuilds ``content/docs`` from
``_rehydrated_posts`` (raw bodies). This module therefore always runs the same
footer and image-caption post-processors used elsewhere so incremental batches
do not strip 原文/图注 styling from the site.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.wechat.wechat_url_stub import canonical_source_url, stub_filename_for_url

REPO_ROOT = Path(__file__).resolve().parents[3]
WECHAT_UPDATE_MANUAL_DIR = Path(__file__).resolve().parent
INPUT_DIR = WECHAT_UPDATE_MANUAL_DIR / "input"
LEGACY_JEKYLL = REPO_ROOT / "_archive" / "legacy-jekyll"
DATA_DIR = LEGACY_JEKYLL / "_data"
MANUAL_YAML = DATA_DIR / "wechat_manual_article_urls.yml"
POSTS_DIR = LEGACY_JEKYLL / "_posts"
CATEGORIES_YML = REPO_ROOT / "data" / "categories.yml"


def load_allowed_slugs(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        out: set[str] = set()
        for row in data:
            if isinstance(row, dict) and row.get("slug"):
                out.add(str(row["slug"]).strip())
        return out
    if isinstance(data, dict):
        return {str(k).strip() for k in data}
    return set()


def warn_unknown_slugs(batch: list[dict], allowed: set[str]) -> None:
    for item in batch:
        slug = item.get("slug")
        if not isinstance(slug, str) or not slug.strip():
            print(f"[warn] batch entry missing slug: {item!r}", flush=True)
            continue
        if allowed and slug.strip() not in allowed:
            print(
                f"[warn] slug {slug.strip()!r} not in data/categories.yml — "
                "Hugo may map it to uncategorized.",
                flush=True,
            )


def normalize_manual_urls(raw: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    if not raw:
        return out
    for k, v in raw.items():
        key = str(k).strip()
        if not key:
            continue
        if isinstance(v, str):
            out[key] = [v]
        elif isinstance(v, list):
            out[key] = [str(x) for x in v if str(x).strip()]
        else:
            out[key] = []
    return out


def merge_batch_into_manual(manual: dict[str, list[str]], batch: list[dict]) -> dict[str, list[str]]:
    merged = {slug: list(urls) for slug, urls in manual.items()}
    for item in batch:
        slug = item.get("slug")
        url_raw = item.get("url")
        if not isinstance(slug, str) or not slug.strip():
            raise ValueError(f"invalid batch entry (slug): {item!r}")
        if not isinstance(url_raw, str) or not url_raw.strip():
            raise ValueError(f"invalid batch entry (url): {item!r}")
        slug = slug.strip()
        canon = canonical_source_url(url_raw)
        if not canon:
            raise ValueError(f"empty url after canonicalize: {item!r}")
        if slug not in merged:
            merged[slug] = []
        existing = {canonical_source_url(u) for u in merged[slug]}
        if canon not in existing:
            merged[slug].append(canon)
    return merged


def load_batch_json(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"batch file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("batch JSON must be a list of {slug, url} objects")
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"batch[{i}] must be an object")
    return data


def run_step(label: str, cmd: list[str]) -> None:
    print("=" * 64, flush=True)
    print(f"{label}: {' '.join(cmd)}", flush=True)
    print("=" * 64, flush=True)
    completed = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge scripts/wechat/update_manual/input/*.json and publish batch to Hugo content/docs.",
    )
    parser.add_argument(
        "batch_id",
        metavar="YYYY-MM-DD",
        help="Batch id matching scripts/wechat/update_manual/input/<id>.json",
    )
    parser.add_argument(
        "--no-skip-existing-rehydrated",
        action="store_true",
        help="Do not pass --skip-if-output-exists to rehydrate_posts.",
    )
    args = parser.parse_args()

    batch_path = INPUT_DIR / f"{args.batch_id}.json"
    batch = load_batch_json(batch_path)

    allowed = load_allowed_slugs(CATEGORIES_YML)
    warn_unknown_slugs(batch, allowed)

    manual_before: dict = {}
    if MANUAL_YAML.exists():
        loaded = yaml.safe_load(MANUAL_YAML.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            manual_before = loaded

    manual_norm = normalize_manual_urls(manual_before)
    merged = merge_batch_into_manual(manual_norm, batch)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MANUAL_YAML.write_text(
        yaml.dump(merged, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(
        f"Wrote {MANUAL_YAML.relative_to(REPO_ROOT)} "
        f"({sum(len(v) for v in merged.values())} total URL row(s) across keys).",
        flush=True,
    )

    py = sys.executable
    run_step(
        "Step 1/5 stubs",
        [py, "-m", "scripts.wechat.migrate", "--stubs-only", "--no-playwright"],
    )

    urls: list[str] = []
    seen: set[str] = set()
    for item in batch:
        u = canonical_source_url(str(item["url"]))
        if u and u not in seen:
            seen.add(u)
            urls.append(u)

    stub_paths: list[Path] = []
    missing: list[str] = []
    for u in urls:
        name = stub_filename_for_url(u)
        candidate = POSTS_DIR / name
        if candidate.is_file():
            stub_paths.append(candidate)
        else:
            missing.append(u)

    if missing:
        print(
            "ERROR: stub file missing for batch URL(s) (migrate did not create expected stub):",
            file=sys.stderr,
            flush=True,
        )
        for u in missing:
            print(f"  {u}", file=sys.stderr, flush=True)
        raise SystemExit(2)

    cmd_re = [py, "-m", "scripts.wechat.rehydrate_posts"]
    for p in stub_paths:
        cmd_re.extend(["--file", str(p)])
    if not args.no_skip_existing_rehydrated:
        cmd_re.append("--skip-if-output-exists")
    run_step("Step 2/5 rehydrate", cmd_re)

    run_step(
        "Step 3/5 Hugo docs (full rebuild from _rehydrated_posts)",
        [py, "-m", "scripts.wechat.migrate_jekyll_to_hugo_book"],
    )

    run_step(
        "Step 4/5 strip WeChat footer + inline 原文链接",
        [py, "-m", "scripts.wechat.normalize_article_footer"],
    )
    run_step(
        "Step 5/5 image lines → centered <figure> captions",
        [py, "-m", "scripts.wechat.postprocess_image_captions"],
    )

    print("Done.", flush=True)


if __name__ == "__main__":
    main()
