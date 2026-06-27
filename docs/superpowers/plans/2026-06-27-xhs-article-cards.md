# XHS Article Cards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate Xiaohongshu slide PNGs from a Hugo article via manifest-driven Python rendering and a repo-committed Cursor Skill for LLM steps.

**Architecture:** Skill writes `manifest.json` + AI `cover-bg.png`; `scripts/xhs/xhs_cards/article.py` parses markdown, paginates verbatim body, renders HTML (cover/body/end), Playwright screenshots. Reuse `base.css` + new `article.css`.

**Tech Stack:** Python 3, PyYAML, Playwright, pytest; Cursor Skill + GenerateImage.

**Spec:** `docs/superpowers/specs/2026-06-27-xhs-article-cards-design.md`

---

### Task 0: Gitignore and track scripts/xhs

**Files:**
- Modify: `.gitignore`
- Add: `scripts/xhs/**` (except output)

- [ ] Change `scripts/xhs/` → `scripts/xhs/output/` in `.gitignore`
- [ ] `git add scripts/xhs .gitignore` and commit

### Task 1: Config and shared helpers

**Files:**
- Create: `scripts/xhs/config.yml`
- Create: `scripts/xhs/xhs_cards/xhs_config.py`

- [ ] Implement `load_xhs_config()`, `load_category_titles()`, `resolve_cta_theme(slug)`
- [ ] Commit

### Task 2: Article parser (TDD)

**Files:**
- Create: `scripts/xhs/xhs_cards/article_parser.py`
- Create: `scripts/xhs/tests/test_article_parser.py`

- [ ] Tests: frontmatter, footer strip, blockquote/paragraph blocks, image warning helper
- [ ] Implement parser using regex from `normalize_article_footer`
- [ ] Commit

### Task 3: Paginator (TDD)

**Files:**
- Create: `scripts/xhs/xhs_cards/article_paginator.py`
- Create: `scripts/xhs/tests/test_article_paginator.py`

- [ ] Tests: paragraph split, long paragraph sentence split, quote integrity
- [ ] Implement `paginate_blocks(blocks, max_chars)`
- [ ] Commit

### Task 4: HTML render + CSS

**Files:**
- Create: `scripts/xhs/xhs_cards/article.css`
- Create: `scripts/xhs/xhs_cards/article.py`
- Create: `scripts/xhs/tests/test_article_render.py`

- [ ] `render_article_slides(manifest_path)` → `(filename, html)` list
- [ ] Cover with `file://` background, body, end slide
- [ ] HTML snapshot tests
- [ ] Commit

### Task 5: CLI integration

**Files:**
- Modify: `scripts/xhs/generate_xhs_cards.py`

- [ ] Add `--series article`, `--manifest`, `--rerender`
- [ ] Commit

### Task 6: Cursor Skill

**Files:**
- Create: `.cursor/skills/xhs-article-cards/SKILL.md`
- Create: `.cursor/skills/xhs-article-cards/examples.md`

- [ ] Full workflow: titles, cover, CTA, manifest, render command
- [ ] Commit

### Task 7: Manual QA

- [ ] Sample manifest + `playwright install chromium` + render Tesla article
- [ ] Adjust `article.css` if text clips
