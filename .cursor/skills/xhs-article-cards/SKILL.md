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
PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/playwright-browsers" \
  .venv/bin/python -m playwright install chromium
```

**Always use the project venv and project Playwright browser cache** when running commands.
Cursor Agent shells may default to system `python3`, and Cursor can set `PLAYWRIGHT_BROWSERS_PATH`
to a temporary sandbox cache. Override it explicitly so Playwright uses the durable browser install
under `.venv/playwright-browsers`:

```bash
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/playwright-browsers"
.venv/bin/python -m scripts.xhs.generate_xhs_cards ...
```

If Playwright reports Chromium missing, first check whether `PLAYWRIGHT_BROWSERS_PATH` points to a
Cursor temp directory. Do not run bare `playwright install chromium`; install with the explicit
project cache command above.

**Body slide header** uses `xhs_title` as the series title (not category label like「阅读书目」). Omit `category_title` from manifest.

**Per article you still need:** user picks a title and one CTA line (`cta_line1`) in manifest.
The cover is **thumbnail-first**: in a Xiaohongshu profile grid, the title must be readable before the background is appreciated.
AI cover backgrounds are optional; use the default paper-style text cover unless the article has a strong visual scene.

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
- Quotes: Songti serif editorial note block, with a quiet paper tint and short bookmark line (not a blue box, not a full-height web blockquote bar).
- Cover: default paper-style typography cover; optional `cover-base.png` can add a quiet mood background. Renderer adds an oversized title layer optimized for profile-grid legibility. Avoid visible white title cards unless a specific cover needs that rescue. `01-cover.png` is the deliverable.
- Cover thumbnail rule: judge the cover at **240-300px wide in a two-column XHS profile grid**, not only as a full 1080x1440 image. The title block should sit around the visual middle, not sink into the lower third; the category label is an editorial marker, not a pill button.
- End slide: theme label + `cta_line1` + @nickname + bio in the card body (no second CTA line).
- **Footer policy:** cover and end have **no slide footer**. Body slides only show **`{n}/{body_total}`** (right-aligned page number, no @nickname watermark).

After `--rerender`, spot-check body slides for clipped text at the bottom border and for quotes that look like two separate boxes on the **same** slide (should not happen after merge step).

Python render:

```bash
PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/playwright-browsers" \
.venv/bin/python -m scripts.xhs.generate_xhs_cards --series article --manifest <path>
```

## Workflow

### 1. Read the article

- Path from user (e.g. `content/docs/2026/06/2026-06-26-yue-du-shu-mu-te-si-la-yu-wai-xing-ren.md`)
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

Default: **skip AI cover generation**. The renderer will create a paper-style typography cover with no `cover-base.png`.

Only generate `cover-base.png` when the article has a strong visual scene that helps recognition (travel, cooking, city life, object/place-specific posts). For reading notes, summaries, and reflective essays, prefer the default text cover.

If generating one, write an image prompt: fresh, soft, reading/life mood; **no readable text**; no faces or important subject details under the future title layer. Treat the AI image as background material, not the information layer.

The rendered cover uses large typography over a soft readability scrim. Prompt the background so it stays quiet behind text:

- low-contrast paper / reading texture, soft light, sparse objects
- avoid high-detail objects, hands, faces, logos, UI screenshots, and dark busy regions
- leave broad clean space through the center/lower half for the title layer
- do not ask the image model to draw Chinese title text; the renderer overlays the real title

If you generated a background, call **GenerateImage**, then **move/copy** the file to:

```
scripts/xhs/output/articles/{output_dir}/cover-base.png
```

The render step composites the title and writes **`01-cover.png`**. Upload `01-cover.png` only; no manual compositing.

If a background exists, use filename **`cover-base.png`** in the manifest (`cover_base` field). If no background exists, omit `cover_base`. Legacy manifests that explicitly declare `cover_ai` or `cover_bg` are still accepted, but new work should not create or rely on `cover-ai.png` / `cover-bg.png`.

`{output_dir}` = **hyphenated pinyin of `original_title`** (文章原标题，不是 markdown 文件名).

Example: `特斯拉与外星人` → `te-si-la-yu-wai-xing-ren`

Compute before creating the folder:

```bash
.venv/bin/python -c "
from pathlib import Path
from scripts.xhs.xhs_cards.article_output_dir import resolve_article_output_dir
print(resolve_article_output_dir(
    '特斯拉与外星人',
    Path('content/docs/2026/06/2026-06-26-yue-du-shu-mu-te-si-la-yu-wai-xing-ren.md'),
))
"
```

If another article already uses the same pinyin folder for a **different** source, the helper appends the post id suffix (e.g. `te-si-la-yu-wai-xing-ren-13f67e2873`).

### 4. CTA theme and copy

**Theme** (`cta_theme`):

| Value | Label | Categories |
|-------|-------|------------|
| `reading` | 读书感悟 | yue-du-shu-mu, du-shu, shu-zhong-jin-ju-fen-xiang, jin-ba-duo-pu-tong-xin-li-xue |
| `summary` | 年度总结 / 总结复盘 | zong-jie |
| `life` | 生活分享 | sheng-huo-ri-ji, di-tie-ri-ji, 30-fen-zhong-ri-ji, xue-zuo-cai, jie-hun-zhe-jian-shi, qin-mi-guan-xi, shen-zhen, zhi-chang-jing-li, ji-shu-bo-ke |

Default from `primary_category` via `scripts/xhs/config.yml` and `resolve_cta_theme()`; override if content clearly fits the other theme.
For `primary_category: zong-jie`, the renderer treats title keywords like「年终」「年度」「年底」「年末」as `年度总结`; other summaries use `总结复盘`.
If a summary article should intentionally show a different label (for example a yearly reading list that should say「读书感悟」), set `cta_label` to the exact display text. Do not rely on a stale `cta_theme: reading` in old manifests as the override signal.

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
  "source": "content/docs/2026/06/2026-06-26-yue-du-shu-mu-te-si-la-yu-wai-xing-ren.md",
  "output_dir": "te-si-la-yu-wai-xing-ren",
  "source_slug": "2026-06-26-yue-du-shu-mu-te-si-la-yu-wai-xing-ren",
  "original_title": "特斯拉与外星人",
  "xhs_title": "<user chosen>",
  "primary_category": "yue-du-shu-mu",
  "cta_theme": "reading",
  "cta_label": "<optional exact label override>",
  "cta_line1": "……",
  "nickname": "我要改名叫嘟嘟",
  "bio": "一个用文字分享生活和读书感悟的程序员",
  "chars_per_slide": 340
}
```

- `output_dir` — folder name under `output/articles/` (pinyin of `original_title`)
- `source_slug` — markdown filename stem (for traceability only)
- `cover_base` — optional; omit for the default paper-style typography cover, set to `"cover-base.png"` only when you generated a background
- `cta_label` — optional exact display override for cover/end theme label; omit in normal cases
- Do **not** set `cover_subtitle`, `category_title`, or `cta_line2` — unused by current renderer

`source` is repo-relative. Pagination fills each slide by **Chromium-measured rendered fit** with **book-style sentence flow**. `chars_per_slide` (default **340**) is kept for manifest compatibility and oversized-block splitting; it is not the primary page-break driver.

Determine `cta_theme` by running (or equivalent logic):

```bash
.venv/bin/python -c "from scripts.xhs.xhs_cards.xhs_config import resolve_cta_theme; print(resolve_cta_theme('yue-du-shu-mu'))"
```

Run from repo root (with venv activated or use `.venv/bin/python`):

```bash
PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/playwright-browsers" \
.venv/bin/python -m scripts.xhs.generate_xhs_cards \
  --series article \
  --manifest scripts/xhs/output/articles/<output_dir>/manifest.json
```

Re-render after CSS or pagination tweaks (keeps manifest + optional cover-base):

```bash
PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/playwright-browsers" \
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
- Upload images **in filename order** (`01-cover.png` … `NN-end.png`); do not upload or expect `cover-ai.png` / `cover-bg.png`
- Use chosen title as the XHS note title
- Path to `post-caption.md`
- Body slide count **varies by article length** — see `examples.md` for a full walk-through sample (not a fixed page target)

### 7. Self-check loop (required before handoff)

After the first render, **always** run QA and fix until acceptable (max **3** repair rounds):

```bash
PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/playwright-browsers" \
.venv/bin/python -m scripts.xhs.xhs_cards.article_qa \
  --manifest scripts/xhs/output/articles/<output_dir>/manifest.json
```

Or combine with render:

```bash
PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/playwright-browsers" \
.venv/bin/python -m scripts.xhs.generate_xhs_cards \
  --series article \
  --manifest scripts/xhs/output/articles/<output_dir>/manifest.json \
  --rerender --qa
```

**Checklist (fix in script/CSS, then `--rerender` again):**

| Check | What to look for | Typical fix |
|-------|------------------|-------------|
| Cover / end footer | **No** `@nickname` or page number on cover or end | `article.py` `_slide_shell(show_page_footer=False)` |
| Cover thumbnail | `01-cover.png` title is readable around 240-300px wide in a two-column profile grid; title block is near the visual middle, not buried in the lower third; category label reads as a marker, not a button | `article.css` cover title scale / vertical placement, or regenerate quieter `cover-base.png` |
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
PLAYWRIGHT_BROWSERS_PATH="$PWD/.venv/playwright-browsers" \
.venv/bin/python -m pytest scripts/xhs/tests/test_article_browser_paginator.py scripts/xhs/tests/test_article_render.py -q
```

## Spec

Full design: `docs/superpowers/specs/2026-06-27-xhs-article-cards-design.md`

## Examples

See `examples.md` in this skill directory.
