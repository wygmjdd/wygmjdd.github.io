---
name: xhs-article-cards
description: >-
  Generate Xiaohongshu slide images from a Hugo content/docs article. Use when
  the user asks to 生成小红书图, xhs cards, or convert a blog article into
  Xiaohongshu images with cover, verbatim body slides, and follow CTA.
---

# Xiaohongshu Article Cards

Turn a Hugo article (`content/docs/.../*.md`) into an ordered PNG series for Xiaohongshu upload.

**Do not** link to WeChat or公众号 on slides or in the post caption.

> **Example vs production:** `examples.md` walks through one article (Tesla reading post) for illustration only. The renderer has **no article-specific logic** — any `content/docs/.../*.md` follows the same workflow below.

## Prerequisites

**One-time setup on each machine** (clone repo → open in Cursor):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
playwright install chromium
```

**Always use the project venv** when running commands (Cursor Agent shells may default to system `python3`):

```bash
source .venv/bin/activate   # then python3 / pip / playwright work
# or explicitly:
.venv/bin/python -m scripts.xhs.generate_xhs_cards ...
```

If Playwright or Python deps are missing, the render command prints install instructions and exits.

**Body slide header** uses `xhs_title` as the series title (not category label like「阅读书目」). Omit `category_title` from manifest.

**Per article you still need:** user picks a title, AI cover (`cover-ai.png`), and one CTA line (`cta_line1`) in manifest.

## Render pipeline (automatic — do not reimplement in Skill)

All body slides are produced by committed Python under `scripts/xhs/xhs_cards/`. When you run `--series article`, the script applies **in order**:

1. **Parse** — `article_parser.py`: paragraphs + blockquotes; strip WeChat footer and **inline `[text](url)` links** (keep anchor text); each markdown paragraph gets a stable `source_id`.
2. **Paginate** — `article_browser_paginator.py`: Chromium measures candidate pages using the same HTML/CSS as final screenshots; paragraphs and quotes may continue on the next slide.
3. **Cleanup page endings** — browser pagination pulls renderable prefixes from the next page when they fit, avoids dangling flow punctuation, and keeps closing punctuation with its text.
4. **Merge blocks** — re-merge adjacent blocks with the same `source_id` on each page.
5. **Render PNG** — `article.py` + `article.css` + Playwright screenshot.
6. **QA loop** — `article_qa.py` (see Step 7); fix errors, and manually review sparse-page warnings.

You do **not** need to hand-tune `chars_per_slide` for normal articles. That value only controls hard-splitting of a single oversized block.

### Pagination behavior (for QA expectations)

| Rule | Detail |
|------|--------|
| Fill strategy | Pack each slide by Chromium-measured rendered fit, not character count. |
| Book flow | Sentences and clauses may continue on the next slide; no「接上页」labels. Never end a mid-paragraph page on `，` when the next slide continues the same source paragraph. |
| Paragraph indent | New markdown paragraphs use `text-indent: 2em`; cross-page continuations use `article-p-continue` (no indent). |
| Paragraph boundaries | **Original markdown paragraphs stay separate** — never merge two source paragraphs into one `<p>`. |
| Quotes | Prefer whole blockquote; split by sentence/clause/chunk only if needed to fit. |
| Last body slide | **May be sparse** (short closing paragraph). Do not sacrifice earlier slides to fill the last one. |
| Overflow | Chromium fit checks are the source of truth; QA uses the same body-fit predicate. |
| Paren-aware split | Sentence splitting respects `（…）` — no orphan `）` fragments. |

### Visual style (`article.css`)

Current article series uses a **warm paper / editorial** look (not glass-on-gradient):

- Body: single full-height paper card; series title in serif + hairline rule.
- Paragraphs: PingFang sans, ~33px, relaxed line-height.
- Quotes: Songti serif, **left accent bar only** (no blue box).
- Cover: `cover-ai.png` background + frosted title card; `01-cover.png` is the deliverable; `cover-bg.png` auto-syncs to match.
- End slide: theme label + `cta_line1` + @nickname + bio in the card body (no second CTA line).
- **Footer policy:** cover and end have **no slide footer**. Body slides only show **`{n}/{body_total}`** (right-aligned page number, no @nickname watermark).

After `--rerender`, spot-check body slides for clipped text at the bottom border and for quotes that look like two separate boxes on the **same** slide (should not happen after merge step).

Python render:

```bash
.venv/bin/python -m scripts.xhs.generate_xhs_cards --series article --manifest <path>
```

## Workflow

### 1. Read the article

- Path from user (e.g. `content/docs/2026/06/reading-category__post-13f67e2873.md`)
- Parse frontmatter: `title`, `primary_category`, `date`
- Resolve `cta_theme` from `primary_category` (category label from `data/categories.yml` is optional context only — **not** shown on body slides)
- Strip trailing「原文链接」footer (same as WeChat normalize patterns)
- If body contains `![](` or `<figure>`, **warn**: v1 slides are text-only

### 2. Title candidates (STOP for user)

Present **3 candidates**. For each:

1. **Title** — XHS note title (may differ from article `title`)
2. **Why it attracts clicks** — 2–3 sentences (hook type, target reader, scroll-stop reason)
3. **Relation to original title** — one line

**Wait** for explicit choice (e.g.「用第 2 个」). Do not render without it.

### 3. Cover background

Write an image prompt: fresh, soft, reading/life mood; **no readable text**; upper area clear for title overlay.

Call **GenerateImage**, then **move/copy** the file to:

```
scripts/xhs/output/articles/{output_dir}/cover-ai.png
```

The render step composites the title onto this image and writes **`01-cover.png`**. After render, **`cover-bg.png` is auto-synced to match `01-cover.png`** — upload `01-cover.png` only; no manual compositing.

Use filename **`cover-ai.png`** in the manifest (`cover_ai` field). Legacy `cover-bg.png`-only folders are still accepted as input but the canonical AI input is `cover-ai.png`.

`{output_dir}` = **hyphenated pinyin of `original_title`** (文章原标题，不是 markdown 文件名).

Example: `特斯拉与外星人` → `te-si-la-yu-wai-xing-ren`

Compute before creating the folder:

```bash
.venv/bin/python -c "
from pathlib import Path
from scripts.xhs.xhs_cards.article_output_dir import resolve_article_output_dir
print(resolve_article_output_dir(
    '特斯拉与外星人',
    Path('content/docs/2026/06/reading-category__post-13f67e2873.md'),
))
"
```

If another article already uses the same pinyin folder for a **different** source, the helper appends the post id suffix (e.g. `te-si-la-yu-wai-xing-ren-13f67e2873`).

### 4. CTA theme and copy

**Theme** (`cta_theme`):

| Value | Label | Categories |
|-------|-------|------------|
| `reading` | 读书感悟 | reading-category, reading, book-quotes-sharing, zimbardo-general-psychology, summary |
| `life` | 生活分享 | life-diary, subway-diary, 30min-diary, learning-to-cook, marriage, intimate-relationships, shenzhen, workplace-experience, technical-blog |

Default from `primary_category` via `scripts/xhs/config.yml` and `resolve_cta_theme()`; override if content clearly fits the other theme.

**One sentence** (article-specific, not generic slogans):

| Field | Rule |
|-------|------|
| `cta_line1` | 共鸣句 — echo insight/feeling from **this** post (book, scene, emotion). No「如果这篇对你有启发」. Do not hint at following/subscribing. |

Fixed on end slide **card body** (not footer): `@我要改名叫嘟嘟` + `一个用文字分享生活和读书感悟的程序员`. Only **`cta_line1`** is shown as the main CTA line (no follow hint / second line).

### 5. Write manifest and render

Create directory: `scripts/xhs/output/articles/{output_dir}/` (pinyin from **`original_title`**, not the Hugo filename).

Write `manifest.json`:

```json
{
  "manifest_version": 1,
  "source": "content/docs/2026/06/reading-category__post-13f67e2873.md",
  "output_dir": "te-si-la-yu-wai-xing-ren",
  "source_slug": "reading-category__post-13f67e2873",
  "original_title": "特斯拉与外星人",
  "xhs_title": "<user chosen>",
  "primary_category": "reading-category",
  "cover_ai": "cover-ai.png",
  "cta_theme": "reading",
  "cta_line1": "……",
  "nickname": "我要改名叫嘟嘟",
  "bio": "一个用文字分享生活和读书感悟的程序员",
  "chars_per_slide": 340
}
```

- `output_dir` — folder name under `output/articles/` (pinyin of `original_title`)
- `source_slug` — markdown filename stem (for traceability only)
- Do **not** set `cover_subtitle`, `category_title`, or `cta_line2` — unused by current renderer

`source` is repo-relative. Pagination fills each slide by **Chromium-measured rendered fit** with **book-style sentence flow**. `chars_per_slide` (default **340**) is kept for manifest compatibility and oversized-block splitting; it is not the primary page-break driver.

Determine `cta_theme` by running (or equivalent logic):

```bash
.venv/bin/python -c "from scripts.xhs.xhs_cards.xhs_config import resolve_cta_theme; print(resolve_cta_theme('reading-category'))"
```

Run from repo root (with venv activated or use `.venv/bin/python`):

```bash
.venv/bin/python -m scripts.xhs.generate_xhs_cards \
  --series article \
  --manifest scripts/xhs/output/articles/<output_dir>/manifest.json
```

Re-render after CSS or pagination tweaks (keeps manifest + cover-ai):

```bash
.venv/bin/python -m scripts.xhs.generate_xhs_cards \
  --series article \
  --manifest scripts/xhs/output/articles/<output_dir>/manifest.json \
  --rerender
```

Stale body PNGs in the output dir are removed automatically when page count changes.

### 6. Deliverables

Write `post-caption.md` in the same output dir:

```markdown
# 小红书标题
{chosen xhs_title}

# 正文说明（可直接粘贴）
{1–2 sentence hook, no external links}

# 话题标签
#读书 #读书笔记 …
```

Tell the user:

- Output folder path
- Upload images **in filename order** (`01-cover.png` … `NN-end.png`); `cover-bg.png` mirrors `01-cover.png` for convenience
- Use chosen title as the XHS note title
- Path to `post-caption.md`
- Body slide count **varies by article length** — see `examples.md` for a full walk-through sample (not a fixed page target)

### 7. Self-check loop (required before handoff)

After the first render, **always** run QA and fix until acceptable (max **3** repair rounds):

```bash
.venv/bin/python -m scripts.xhs.xhs_cards.article_qa \
  --manifest scripts/xhs/output/articles/<output_dir>/manifest.json
```

Or combine with render:

```bash
.venv/bin/python -m scripts.xhs.generate_xhs_cards \
  --series article \
  --manifest scripts/xhs/output/articles/<output_dir>/manifest.json \
  --rerender --qa
```

**Checklist (fix in script/CSS, then `--rerender` again):**

| Check | What to look for | Typical fix |
|-------|------------------|-------------|
| Cover / end footer | **No** `@nickname` or page number on cover or end | `article.py` `_slide_shell(show_page_footer=False)` |
| Body links | No `[文字](url)` or `<a href` in slide text — anchor text only | `article_parser.strip_inline_markdown_links` |
| Body footer | `@nickname` bottom-left + `1/N` … `N/N` bottom-right (N = body page count only) | `article.py` body footer, `article.css` |
| Page fill | Body slides mostly full; only the **last** body slide may be sparse. A small QA underfill warning is acceptable after visual review when the next line would overflow. | `article_browser_paginator.py` |
| Overflow | No text visibly clipped at bottom border | `_BODY_FITS_JS` in `article_browser_paginator.py` |
| Quote blocks | One quote box per source quote on the same slide | `_merge_adjacent_blocks` |

**Loop:**

1. Run QA (`article_qa` or `--qa`).
2. If **errors** remain, diagnose (parser / browser paginator / CSS), patch scripts, `--rerender`.
3. If only **underfill warnings** remain, visually inspect the named slides and the next slide. Accept them if the next visible line would not fit without clipping or awkward punctuation.
4. Re-run QA after fixes. Repeat until no errors, or after 3 repair rounds report remaining issues to the user with slide filenames.

Exit codes: `0` pass, `1` errors, `2` warnings only. `2` can be acceptable after visual review; do not claim fully clean QA if warnings remain.

## Key modules (for debugging)

| Module | Role |
|--------|------|
| `article_parser.py` | Markdown → blocks; `source_id` per paragraph/quote |
| `article_browser_paginator.py` | Default Chromium-measured body pagination and page-ending cleanup |
| `article_paginator.py` | Legacy text splitting helpers reused by browser paginator |
| `article_overflow.py` | QA overflow predicate compatibility |
| `article_qa.py` | Post-render QA checklist (links, fill, overflow) |
| `article.css` | Paper editorial visual system |
| `tests/test_article_browser_paginator.py` | Browser pagination regressions |
| `tests/test_article_paginator.py` | Legacy splitter, paragraph boundaries, quote merge |

Run tests after pagination/CSS changes:

```bash
.venv/bin/python -m pytest scripts/xhs/tests/test_article_browser_paginator.py scripts/xhs/tests/test_article_render.py -q
```

## Spec

Full design: `docs/superpowers/specs/2026-06-27-xhs-article-cards-design.md`

## Examples

See `examples.md` in this skill directory.
