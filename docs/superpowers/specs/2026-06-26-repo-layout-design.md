# Repository layout reorganization

**Date:** 2026-06-26  
**Status:** Approved (reviewed)  
**Goal:** Clean repo root, business-scoped `scripts/` packages, Hugo `data/` only for site runtime data.

## Problem

The repository mixes Hugo site files with local tooling at the root:

- `update_manual/` — Python package for the WeChat migration pipeline, unrelated to Hugo
- `output/` — Xiaohongshu card generator artifacts
- `data/reading_inventory.json` — script input sitting beside Hugo's `data/categories.yml`
- `scripts/` — flat list of 14+ Python files spanning two unrelated workflows

Hugo requires `content/` and `data/` at the repo root with specific semantics. The confusion is not that `content` and `data` should merge, but that non-Hugo data was placed under Hugo's `data/` directory.

## Principles

1. **Preserve Hugo conventions** — `content/`, `data/categories.yml`, `layouts/`, `assets/`, `static/`, `hugo.toml` stay at root with unchanged meaning.
2. **Clean root** — only Hugo dirs, `scripts/`, `docs/`, and standard repo files at top level.
3. **Business-scoped scripts** — `scripts/wechat/` (migration pipeline) and `scripts/xhs/` (local card generation) are separate packages.
4. **Explicit invocation** — no root-level shims; run via `python3 -m scripts.<package>.<module>` from repo root.
5. **Minimal scope** — move files and update paths/imports/docs only; no script logic refactors.

## Target layout

```
wygmjdd.github.io/
├── content/                    # Hugo pages (unchanged)
├── data/
│   └── categories.yml          # Hugo only (site.Data.categories)
├── layouts/ assets/ static/ hugo.toml go.mod ...
├── docs/
├── scripts/
│   ├── requirements.txt        # shared deps (wechat + xhs)
│   ├── wechat/
│   │   ├── __init__.py
│   │   ├── migrate.py
│   │   ├── rehydrate_posts.py
│   │   ├── migrate_jekyll_to_hugo_book.py
│   │   ├── normalize_article_footer.py
│   │   ├── postprocess_image_captions.py
│   │   ├── fetch_article.py
│   │   ├── parse_album.py
│   │   ├── slug_from_album.py
│   │   ├── wechat_url_stub.py
│   │   ├── update_manual/
│   │   │   ├── __init__.py
│   │   │   └── __main__.py
│   │   ├── tests/
│   │   │   ├── test_fetch_article.py
│   │   │   ├── test_normalize_article_footer.py
│   │   │   ├── test_rehydrate_posts.py
│   │   │   └── test_slug.py
│   │   ├── MANUAL_URLS.md
│   │   ├── rehydrate_skipped.yml   # tracked; failure retry log
│   │   └── .migrate_done           # runtime state (gitignored)
│   └── xhs/                        # tracked in git; generated output gitignored
│       ├── __init__.py
│       ├── generate_xhs_cards.py
│       ├── config.yml
│       ├── xhs_cards/
│       │   ├── __init__.py
│       │   ├── series_a.py
│       │   ├── series_6years.py
│       │   ├── article.py          # article series (added 2026-06-27)
│       │   ├── base.css
│       │   └── six_years.css
│       ├── data/
│       │   └── reading_inventory.json
│       ├── tests/
│       └── output/                 # gitignored (PNGs only)
│           ├── 6-years-updating.png
│           └── series-a/
├── .cursor/skills/xhs-article-cards/   # Cursor Skill (added 2026-06-27)
└── _archive/                       # gitignored (unchanged)
```

**Removed from root:** `update_manual/`, `output/`  
**Removed from `scripts/` root:** all flat `*.py`, `test_*.py`, `MANUAL_URLS.md`, `rehydrate_skipped.yml` (relocated under `scripts/wechat/`)  
**Moved (local filesystem, not committed):** `data/reading_inventory.json` → `scripts/xhs/data/`; `output/**` → `scripts/xhs/output/**`  
**Unchanged Hugo paths:** `data/categories.yml`, `content/docs/`, `_archive/legacy-jekyll/`

## What is committed vs local-only

| Path | In git after reorg |
|------|-------------------|
| `scripts/wechat/**` | Yes — use `git mv` for tracked files to preserve history |
| `scripts/requirements.txt` | Yes — stays at `scripts/requirements.txt` |
| `scripts/xhs/**` (source, tests, `data/`, Skill) | Yes — committed from 2026-06-27 (`640d178` and follow-ups) |
| `scripts/xhs/output/**` | No — gitignored (generated PNGs) |
| `.cursor/skills/xhs-article-cards/` | Yes — repo-committed Cursor Skill |
| Root `update_manual/`, `output/`, `data/reading_inventory.json` | Removed from tree / never committed |

The initial implementation commit (`f10cdd3`) covered **wechat reorg only**. XHS was moved locally first; **xhs source + Skill were later committed** so a second machine can clone and use the article card pipeline without restoring from backup.

## CLI commands (from repo root)

| Task | Command |
|------|---------|
| Manual batch update | `python3 -m scripts.wechat.update_manual 2026-05-26` |
| Album → stubs | `python3 -m scripts.wechat.migrate --stubs-only` |
| Rehydrate posts | `python3 -m scripts.wechat.rehydrate_posts` |
| Archive → Hugo docs | `python3 -m scripts.wechat.migrate_jekyll_to_hugo_book` |
| Footer normalization | `python3 -m scripts.wechat.normalize_article_footer` |
| Image caption postprocess | `python3 -m scripts.wechat.postprocess_image_captions` |
| XHS card generation | `python3 -m scripts.xhs.generate_xhs_cards` |

No root-level forwarding entry points. `update_manual` subprocess calls use the same `-m scripts.wechat.*` form (not file paths like `scripts/wechat/migrate.py`).

**Prerequisite:** commands are run from the repository root so Python resolves the `scripts` package (cwd is on `sys.path`).

## Package and import conventions

- Add `scripts/__init__.py`, `scripts/wechat/__init__.py`, `scripts/xhs/__init__.py`, `scripts/xhs/xhs_cards/__init__.py`.
- Remove all `sys.path.insert` hacks; use absolute imports, e.g. `from scripts.wechat.fetch_article import fetch_article`.
- `REPO_ROOT` = repository root (`parents[2]` from modules directly under `scripts/wechat/`; `parents[3]` from `scripts/wechat/update_manual/__main__.py`).
- Wechat path constants to update:

| Constant | Old path | New path |
|----------|----------|----------|
| `DONE_FILE` | `scripts/.migrate_done` | `scripts/wechat/.migrate_done` |
| `DEFAULT_LOG_PATH` | `scripts/rehydrate_skipped.yml` | `scripts/wechat/rehydrate_skipped.yml` |
| Manual URL fallback | `scripts/manual_article_urls.yml` | `scripts/wechat/manual_article_urls.yml` |

- Hugo-facing paths unchanged: `data/categories.yml`, `content/docs/`, `_archive/legacy-jekyll/...`, `static/images/wechat/`. Env var `WYGMJDD_POSTS_DIR` behavior unchanged.
- XHS paths are package-local (no `REPO_ROOT` for data/output):

| Constant | New path |
|----------|----------|
| Reading inventory | `scripts/xhs/data/reading_inventory.json` |
| Series A output | `scripts/xhs/output/series-a/` |
| 6-years infographic | `scripts/xhs/output/6-years-updating.png` |

`series_a.py` reads inventory relative to the `xhs` package (`Path(__file__).resolve().parent.parent / "data" / ...`), not repo-root `data/`.

## `.gitignore` changes

Initial reorg (2026-06-26):

```gitignore
scripts/wechat/.migrate_done
scripts/xhs/
```

**Amended 2026-06-27** (xhs article cards): only generated output is ignored:

```gitignore
scripts/wechat/.migrate_done
scripts/xhs/output/
```

Remove these obsolete entries:

```gitignore
scripts/.migrate_done
output/
data/reading_inventory.json
scripts/generate_xhs_cards.py
scripts/xhs_cards/
```

## Documentation updates

| File | Change |
|------|--------|
| `docs/迁移脚本说明.md` | All commands → `python3 -m scripts.wechat.*`; update paths for `.migrate_done`, `rehydrate_skipped.yml`, `manual_article_urls.yml`; fix footer note to reference `-m` form |
| `docs/hugo-and-archive.md` | Fix `categories.yml` to `data/categories.yml`; update script paths to `scripts/wechat/...` |
| `scripts/wechat/MANUAL_URLS.md` | Update optional fallback path to `scripts/wechat/manual_article_urls.yml` |
| `scripts/wechat/*.py` | Update module docstrings and argparse `help`/`epilog` strings that mention old `scripts/...` paths |

**Not updated (historical records):** `docs/plans/*`, `docs/superpowers/specs/2026-06-05-article-footer-date-design.md` — left as-is; they describe the state at time of writing.

## Implementation sequence

1. Create `scripts/__init__.py`, `scripts/wechat/`, `scripts/wechat/tests/`, `scripts/wechat/update_manual/`.
2. `git mv` all tracked wechat files from `scripts/` and `update_manual/` into `scripts/wechat/` (preserve history).
3. Add package `__init__.py` files; fix imports, `REPO_ROOT`, and path constants per table above.
4. Rewrite `update_manual` subprocess calls to `python3 -m scripts.wechat.<module>`.
5. Update test imports to `from scripts.wechat.<module> import ...`.
6. Locally move xhs files into `scripts/xhs/` and fix xhs paths (not part of git commit).
7. Update `.gitignore` and documentation files listed above.
8. Delete any leftover empty dirs (`update_manual/`, root `output/`).
9. Run verification checklist.

## Out of scope

- Hugo templates, `hugo.toml`, GitHub Actions workflow (no script paths referenced)
- Changes to `categories.yml` content
- Internal logic refactors of migration scripts (beyond path/import/docstring updates)
- ~~Committing `scripts/xhs/` artifacts or source~~ — **superseded:** xhs source + Skill are now committed; only `scripts/xhs/output/` stays local
- Rewriting historical specs under `docs/plans/` or older `docs/superpowers/specs/`

## Verification

1. `pytest scripts/wechat/tests/ -v` passes from repo root with venv active.
2. Each wechat module runs without import errors, e.g. `python3 -m scripts.wechat.migrate --help`.
3. `python3 -m scripts.wechat.update_manual --help` works.
4. `git status` shows no root-level `update_manual/`, `output/`, or `data/reading_inventory.json`.
5. `git ls-files scripts/` lists only `scripts/__init__.py`, `scripts/requirements.txt`, and `scripts/wechat/**` (no flat `scripts/*.py`).
6. Hugo build unchanged: `hugo --minify --gc --buildFuture` (optional smoke check).
7. (Local) `python3 -m scripts.xhs.generate_xhs_cards --help` runs after xhs filesystem move.
8. `pytest scripts/xhs/tests/ -q` passes; article series: see `docs/superpowers/specs/2026-06-27-xhs-article-cards-design.md`.

## Amendments (2026-06-27)

After the xhs **article cards** feature (`docs/superpowers/specs/2026-06-27-xhs-article-cards-design.md`):

1. **`scripts/xhs/` is tracked in git** — Python package, `config.yml`, `data/reading_inventory.json`, tests.
2. **Only `scripts/xhs/output/` is gitignored** — generated PNGs and per-article manifests under `output/articles/`.
3. **`.cursor/skills/xhs-article-cards/`** — committed for cross-machine Cursor use.
4. **Article series CLI:** `python3 -m scripts.xhs.generate_xhs_cards --series article --manifest <path>`.

Historical sections above that say「xhs 整树 gitignore」describe the **2026-06-26 reorg intent** before this amendment.

## Migration notes for local machines

After pulling the reorganization:

- Move `output/**` → `scripts/xhs/output/**` (flatten `output/xhs/series-a/` → `scripts/xhs/output/series-a/`; include drafts like `6-years-updating.md` if present).
- Move `data/reading_inventory.json` → `scripts/xhs/data/` if present.
- Move existing `scripts/.migrate_done` → `scripts/wechat/.migrate_done` if present.
- Update shell aliases from `python3 -m update_manual` to `python3 -m scripts.wechat.update_manual`.
- Re-run `pip install -r scripts/requirements.txt` if needed (path unchanged).
