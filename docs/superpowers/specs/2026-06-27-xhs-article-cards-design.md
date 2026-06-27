# Xiaohongshu article card generator (Skill + script)

**Date:** 2026-06-27  
**Status:** Approved  
**Goal:** From a Hugo `content/docs/` article, produce a Xiaohongshu-ready image series (cover + verbatim body slides + follow CTA slide) via a **repo-committed Cursor Skill** and a **Python render script**.

## Problem

Articles are currently copy-pasted into Xiaohongshu as plain text. Engagement is low. Aside from content quality, the presentation lacks:

- A click-worthy cover and marketing title
- Consistent, fresh multi-slide layout (1080×1440)
- A platform-native closing slide that encourages **follow on Xiaohongshu only** (no WeChat引流 — XHS penalizes external links)

The repo already has `scripts/xhs/` with Playwright HTML→PNG rendering and a warm typography design system (`base.css`, 1080×1440). That pipeline serves **reading inventory infographics**, not single-article slides.

## Repo constraint (must fix during implementation)

Today `.gitignore` ignores the **entire** `scripts/xhs/` tree, and none of it is tracked in git. That conflicts with shipping the article renderer and using it on a second machine.

**Implementation step 0:** change `.gitignore` to ignore only generated artifacts:

```gitignore
# Xiaohongshu generated output (local)
scripts/xhs/output/
```

Then **commit** (at minimum):

- `scripts/xhs/` Python package (`generate_xhs_cards.py`, `xhs_cards/`, `config.yml`, `tests/`)
- `scripts/xhs/data/reading_inventory.json` (existing series-a input; already in workspace)
- `.cursor/skills/xhs-article-cards/`

Keep **`scripts/xhs/output/`** gitignored.

## Decisions (confirmed)

| Topic | Decision |
|-------|----------|
| XHS title | **3 candidates** with rationale; user picks one before render |
| Cover | **AI background** (Cursor `GenerateImage`) + **script typography overlay** |
| Body slides | **Verbatim** article text; strip Hugo「原文链接，更新于…」footer only |
| Closing slide | Extra page; **follow XHS only**, no公众号 |
| CTA theme | Two directions: **读书感悟** / **生活分享**, mapped from `primary_category` (Skill may override) |
| CTA copy | **Two article-specific sentences** (共鸣句 + 关注理由), not generic slogans |
| Interaction | **Full Cursor workflow**: user points at `.md`, Skill orchestrates end-to-end |
| Re-render | **`manifest.json`** on disk; script supports `--rerender` without re-running LLM |
| Skill location | **Committed in this repo** (`.cursor/skills/`) for use on a second machine |

## Principles

1. **Skill for judgment, script for determinism** — titles, cover prompt, CTA copy, hashtags: Skill (LLM). Pagination, HTML, PNG: Python + Playwright.
2. **Verbatim body** — no summarization on content slides; only pagination and styling.
3. **Platform-safe引流** — no WeChat links on slides or suggested post caption.
4. **Reuse existing visual system** — extend `base.css`; same viewport and `@我要改名叫嘟嘟` footer pattern as series-a.
5. **Repo-portable** — Skill + script + config tracked in git; generated PNGs under `scripts/xhs/output/` (gitignored).

## Prerequisites

From repo root on any machine:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
playwright install chromium
```

Open the repo in Cursor. Invoke the skill explicitly (see Skill metadata below).

## Architecture

```mermaid
flowchart LR
  A[User: article .md path] --> B[Skill: parse article]
  B --> C[Skill: 3 titles + 引流 rationale]
  C --> D[User picks title]
  D --> E[Skill: cover image prompt + GenerateImage]
  E --> F[Skill: CTA theme + 2 contextual lines]
  F --> G[Skill: write manifest.json + post-caption.md]
  G --> H["python3 -m scripts.xhs.generate_xhs_cards --series article"]
  H --> I["output/articles/{slug}/*.png"]
```

### Components

| Component | Path | Role |
|-----------|------|------|
| Cursor Skill | `.cursor/skills/xhs-article-cards/SKILL.md` | Orchestration, LLM steps, user gates |
| Render CLI | `scripts/xhs/generate_xhs_cards.py` | Add `--series article`, `--manifest`, `--rerender` |
| Article module | `scripts/xhs/xhs_cards/article.py` | Parse md, paginate, render HTML slides |
| Styles | `scripts/xhs/xhs_cards/article.css` | Body + cover overlay + end slide (extends `base.css`) |
| Config | `scripts/xhs/config.yml` | nickname, bio, chars-per-slide, CTA category mapping |
| Category titles | `data/categories.yml` | Hugo source of truth for Chinese category names (cover chip, slide header) |
| Manifest | `scripts/xhs/output/articles/{slug}/manifest.json` | Single source of truth for one generation run |
| Tests | `scripts/xhs/tests/test_article_*.py` | Paginator + HTML snapshot (no Playwright in CI) |

## Skill workflow

**Trigger phrases:** 「生成小红书图」「xhs cards」「把这篇生成小红书图」+ path to `content/docs/.../*.md`.

**Skill metadata** (in `SKILL.md` frontmatter):

- `name: xhs-article-cards`
- `description:` generate Xiaohongshu slide images from a Hugo article path
- `disable-model-invocation: true` — only run when user explicitly asks

### Step 1 — Read article

- Parse YAML frontmatter: `title`, `date`, `primary_category`, optional `source_url`
- Resolve **category display title** from `data/categories.yml` by `primary_category` slug
- Read body; strip trailing inline footer using the same patterns as `scripts/wechat/normalize_article_footer.py` (`<small>（<a …>原文链接</a>…）</small>`, promo `↓↓↓` lines, `article-follow-cta` divs)
- **v1 text-only:** if body contains `<figure>` or `![](` image markdown, **warn** the user that images are omitted on slides; do not fail silently

### Step 2 — Title candidates (user gate)

Output **3 candidates**. Each includes:

1. **Title text** (XHS note title; may differ from `title` in frontmatter)
2. **Why it attracts clicks** — 2–3 sentences: hook type (curiosity, contrast, specificity, emotion), target reader, scroll-stop reason
3. **Relation to original title** — one line

Wait for user to pick (e.g.「用第 2 个」). Do not proceed without an explicit choice.

### Step 3 — Cover background

- Skill writes an image prompt: fresh, soft, reading/life mood matching article; **no readable text in image**; leave negative space for title overlay (upper half)
- Call `GenerateImage`; move/copy the result into the output dir as `cover-bg.png` (must exist before Step 5; re-use this file on `--rerender`)

### Step 4 — CTA theme and copy

**Theme selection (`cta_theme`):**

| Value | Display label | Default categories (see config) |
|-------|---------------|----------------------------------|
| `reading` | 读书感悟 | reading-category, reading, book-quotes-sharing, zimbardo-general-psychology, summary |
| `life` | 生活分享 | life-diary, subway-diary, 30min-diary, learning-to-cook, marriage, intimate-relationships, shenzhen, workplace-experience, technical-blog |

- Default from `primary_category` via `scripts/xhs/config.yml`
- Skill may override when article content clearly fits the other theme

**Closing slide copy (article-specific):**

| Line | Purpose | Rules |
|------|---------|-------|
| **Line 1 — 共鸣句** | Echo a feeling, question, or insight from *this* post | May paraphrase; must reference concrete details (book, scene, emotion). No generic「如果这篇对你有启发」. |
| **Line 2 — 关注理由** | Natural bridge to following | Describe what *similar* content follows; soft CTA. Do not use「关注我，持续分享…」as the whole sentence. |

**Fixed on end slide (always rendered by script):**

- `@我要改名叫嘟嘟`
- `一个用文字分享生活和读书感悟的程序员`

**Examples (读书感悟 / Tesla article):**

- Line 1: 「读完《特斯拉自传》，我对《外星人访谈录》里『现在-成为者』的着迷，祛魅不少。」
- Line 2: 「如果你也容易被『厉害到不像人』的故事吸住，我会继续把读书时的惊讶和笔记写下来。」

**Examples (生活分享 / subway-diary):**

- Line 1: 「今天地铁上又发生了一件小事，不写下来明天可能就忘了。」
- Line 2: 「我喜欢把这些真实的日常片段留住——如果你也想看一个程序员的生活切面，欢迎留下来。」

### Step 5 — Write manifest and render

1. Create `scripts/xhs/output/articles/{slug}/` where `{slug}` = markdown filename stem (e.g. `reading-category__post-13f67e2873`)
2. Write `manifest.json` (schema below)
3. Run from repo root:

```bash
python3 -m scripts.xhs.generate_xhs_cards \
  --series article \
  --manifest scripts/xhs/output/articles/<slug>/manifest.json
```

**`--rerender`:** re-read `manifest.json` and `source` article; regenerate PNGs only. Do not call `GenerateImage`. Fail if `cover-bg.png` is missing.

### Step 6 — Deliverables

Skill writes `post-caption.md` in the output dir:

```markdown
# 小红书标题
{chosen xhs_title}

# 正文说明（可直接粘贴）
{1–2 sentence hook, no external links}

# 话题标签
#读书 #读书笔记 #特斯拉 …
```

Print to user:

- Output directory and ordered file list
- Path to `post-caption.md`
- Reminder: upload images **in filename order**; use chosen title as note title

## Body slide rules

- **Verbatim** paragraphs and blockquotes after footer strip
- **Pagination:** split at paragraph boundaries; target `chars_per_slide` from config (default **270**). Count includes Chinese characters and punctuation; exclude leading/trailing whitespace on each chunk
- **Long paragraph:** if one paragraph exceeds limit, split at sentence boundaries (`。！？；`) before hard-splitting mid-sentence
- **Blockquotes** (`>` lines): prefer keeping a quote block on one slide; if too long, split at sentence boundaries inside the quote
- **Slide header (body pages):** Chinese category title from `data/categories.yml` (e.g. `阅读书目`)
- **Footer on every slide:** `@我要改名叫嘟嘟` + `{page}/{total}` where **total = cover + body pages + end slide**
- **No** WeChat URLs or「原文链接」on any slide

### Overflow safety

After HTML layout, Playwright screenshot must not clip text. If a page overflows in manual QA:

1. Lower effective chars for that article via manifest override `chars_per_slide`, or
2. Adjust `article.css` font size (global fix)

Script does not auto-detect overflow in v1; manual QA on first article is required.

## Slide sequence and naming

| Order | Filename | Content | Page footer |
|-------|----------|---------|-------------|
| 1 | `01-cover.png` | AI `cover-bg.png` + overlay: XHS title, `cover_subtitle`, category chip | `1/{total}` |
| 2 … N−1 | `02.png`, `03.png`, … | Body pages (zero-padded) | `2/{total}` … |
| N | `{NN}-end.png` | CTA lines + @nickname + bio | `{total}/{total}` |

**Cover overlay fields** (from manifest):

- `xhs_title` — main large title
- `cover_subtitle` — Skill chooses: original `title`, or one short hook sentence (≤ 20 chars preferred)
- `category_title` — Chinese label from `data/categories.yml`

## Manifest schema

```json
{
  "manifest_version": 1,
  "source": "content/docs/2026/06/reading-category__post-13f67e2873.md",
  "slug": "reading-category__post-13f67e2873",
  "original_title": "特斯拉与外星人",
  "xhs_title": "读《特斯拉自传》后，我对外星人祛魅了",
  "cover_subtitle": "特斯拉与外星人",
  "primary_category": "reading-category",
  "category_title": "阅读书目",
  "cover_bg": "cover-bg.png",
  "cta_theme": "reading",
  "cta_line1": "……",
  "cta_line2": "……",
  "nickname": "我要改名叫嘟嘟",
  "bio": "一个用文字分享生活和读书感悟的程序员",
  "chars_per_slide": 200
}
```

- Paths (`source`, `cover_bg`) are **repo-relative** for `source`; **manifest-dir-relative** for `cover_bg`
- Script resolves repo root from `scripts/xhs/` (e.g. `Path(__file__).resolve().parents[2]`) and joins `source`
- `nickname`, `bio`, and `chars_per_slide` in manifest **override** `config.yml`; omit them to use config defaults

## Config (`scripts/xhs/config.yml`)

```yaml
nickname: 我要改名叫嘟嘟
bio: 一个用文字分享生活和读书感悟的程序员
chars_per_slide: 270
default_cta: reading
cta_mapping:
  reading:
    - reading-category
    - reading
    - book-quotes-sharing
    - zimbardo-general-psychology
    - summary
  life:
    - life-diary
    - subway-diary
    - 30min-diary
    - learning-to-cook
    - marriage
    - intimate-relationships
    - shenzhen
    - workplace-experience
    - technical-blog
```

Unlisted `primary_category` values fall back to `default_cta`. Skill may set `cta_theme` in manifest regardless.

Category **display titles** are resolved at render time from `data/categories.yml` when `category_title` is omitted in manifest (via `primary_category` on the article or manifest).

## Output layout

```
scripts/xhs/output/articles/reading-category__post-13f67e2873/
  manifest.json
  cover-bg.png          # AI input; kept for --rerender
  post-caption.md       # Skill-written; not used by script
  01-cover.png
  02.png
  03.png
  …
  08-end.png
```

`scripts/xhs/output/` remains gitignored.

## Skill repo layout (committed)

```
.cursor/skills/xhs-article-cards/
  SKILL.md              # triggers, steps, manifest fields, CTA rules, CLI commands
  examples.md           # walk-through with Tesla article (recommended)
```

Cursor loads project skills from `.cursor/skills/` when the repo is opened. On a second machine: clone, open repo in Cursor, invoke by name or trigger phrase.

## Error handling

| Condition | Behavior |
|-----------|----------|
| Missing article path | Skill stops with clear error |
| User has not picked title | Do not render |
| `cover-bg.png` missing at render time | Script error with path |
| Playwright / browser missing | Script exits with `playwright install chromium` hint |
| Body empty after strip | Skill stops |
| `--rerender` without manifest | Script error |
| Unknown `primary_category` slug | Use slug as fallback chip text; log warning |

## Testing

- `test_article_parser.py` — frontmatter, footer strip, blockquote blocks
- `test_article_paginator.py` — paragraph/sentence splits, char limits, quote integrity
- `test_article_render.py` — HTML contains expected chunks; cover/end slide markers

Run: `python3 -m pytest scripts/xhs/tests/ -q` from repo root (with venv).

Manual QA: Skill on `reading-category__post-13f67e2873.md` — verify ~10–12 slides at default 270 chars, no clipped text, cover title readable on AI background.

## Out of scope (v1)

- Auto-posting to Xiaohongshu
- 公众号 QR codes or links on slides or in `post-caption.md`
- Embedding WeChat article images in body slides
- Multiple visual themes per category
- AI-generated body slide backgrounds
- Batch processing many articles in one command
- Auto overflow detection / dynamic font scaling

## Implementation order

0. Fix `.gitignore`; commit existing `scripts/xhs/` sources + `data/`
1. `config.yml` + category mapping helpers (read `data/categories.yml`)
2. `article.py` — parser (footer strip: reuse or share regex from `normalize_article_footer`), paginator, HTML render
3. Extend `generate_xhs_cards.py` — add `--series article` alongside existing `a` / `6years` (unchanged)
4. Tests
5. `.cursor/skills/xhs-article-cards/SKILL.md` (+ `examples.md`)
6. Manual run on Tesla article; iterate `article.css` if needed

## Self-review checklist

- [x] No TBD sections
- [x] `.gitignore` conflict documented with fix (step 0)
- [x] Skill committed in repo (`.cursor/skills/`)
- [x] CTA: two article-specific sentences + fixed @nickname/bio
- [x] No公众号引流 on slides or caption
- [x] Manifest fields complete (subtitle, category, chars override)
- [x] Slide header, page numbering, filename convention explicit
- [x] `--rerender` behavior defined
- [x] Prerequisites (venv, playwright) documented
- [x] v1 limits (no inline images) stated
- [x] All `data/categories.yml` slugs mapped in `cta_mapping`
