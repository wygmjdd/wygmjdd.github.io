---
name: xhs-article-cards
description: >-
  Generate Xiaohongshu slide images from a Hugo content/docs article. Use when
  the user asks to 生成小红书图, xhs cards, or convert a blog article into
  Xiaohongshu images with cover, verbatim body slides, and follow CTA.
disable-model-invocation: true
---

# Xiaohongshu Article Cards

Turn a Hugo article (`content/docs/.../*.md`) into an ordered PNG series for Xiaohongshu upload.

**Do not** link to WeChat or公众号 on slides or in the post caption.

## Prerequisites

- Repo root with venv: `pip install -r scripts/requirements.txt` && `playwright install chromium`
- Python render: `python3 -m scripts.xhs.generate_xhs_cards --series article --manifest <path>`

## Workflow

### 1. Read the article

- Path from user (e.g. `content/docs/2026/06/reading-category__post-13f67e2873.md`)
- Parse frontmatter: `title`, `primary_category`, `date`
- Load Chinese category title from `data/categories.yml`
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
scripts/xhs/output/articles/{slug}/cover-bg.png
```

`{slug}` = markdown filename stem (e.g. `reading-category__post-13f67e2873`).

### 4. CTA theme and copy

**Theme** (`cta_theme`):

| Value | Label | Categories |
|-------|-------|------------|
| `reading` | 读书感悟 | reading-category, reading, book-quotes-sharing, zimbardo-general-psychology, summary |
| `life` | 生活分享 | life-diary, subway-diary, 30min-diary, learning-to-cook, marriage, intimate-relationships, shenzhen, workplace-experience, technical-blog |

Default from `primary_category` via `scripts/xhs/config.yml`; override if content clearly fits the other theme.

**Two sentences** (article-specific, not generic slogans):

| Field | Rule |
|-------|------|
| `cta_line1` | 共鸣句 — echo insight/feeling from **this** post (book, scene, emotion). No「如果这篇对你有启发」. |
| `cta_line2` | 关注理由 — what similar content follows; soft follow CTA. Do not end with only「关注我，持续分享…」. |

Fixed on end slide (script renders): `@我要改名叫嘟嘟` + `一个用文字分享生活和读书感悟的程序员`.

### 5. Write manifest and render

Create directory: `scripts/xhs/output/articles/{slug}/`

Write `manifest.json`:

```json
{
  "manifest_version": 1,
  "source": "content/docs/2026/06/reading-category__post-13f67e2873.md",
  "slug": "reading-category__post-13f67e2873",
  "original_title": "特斯拉与外星人",
  "xhs_title": "<user chosen>",
  "cover_subtitle": "<original title or short hook, ≤20 chars preferred>",
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

`source` is repo-relative. Run from repo root:

```bash
python3 -m scripts.xhs.generate_xhs_cards \
  --series article \
  --manifest scripts/xhs/output/articles/<slug>/manifest.json
```

Re-render after CSS tweaks (keeps manifest + cover-bg):

```bash
python3 -m scripts.xhs.generate_xhs_cards \
  --series article \
  --manifest scripts/xhs/output/articles/<slug>/manifest.json \
  --rerender
```

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
- Upload images **in filename order** (`01-cover.png` … `NN-end.png`)
- Use chosen title as the XHS note title
- Path to `post-caption.md`

## Spec

Full design: `docs/superpowers/specs/2026-06-27-xhs-article-cards-design.md`

## Examples

See `examples.md` in this skill directory.
