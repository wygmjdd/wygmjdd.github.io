# Example walk-through (one article)

This file illustrates the Skill workflow end-to-end. **The scripts treat every article the same** — nothing here is special-cased in code.

**Article:** `content/docs/2026/06/reading-category__post-13f67e2873.md`  
**Output dir (this run):** `reading-category__post-13f67e2873` — legacy slug folder from an early run. **New articles** should use hyphenated pinyin of `original_title` (see `SKILL.md` → `resolve_article_output_dir`), e.g. `te-si-la-yu-wai-xing-ren`.
**Source slug:** `reading-category__post-13f67e2873` (markdown filename stem; traceability only)

## Sample title candidates

### 候选 1

**标题：** 读《特斯拉自传》后，我对外星人祛魅了

**为什么吸引人：** 用「祛魅」制造反差——读者以为会是科幻猎奇，结果是真实传记带来的认知反转。目标读者：对特斯拉、外星人、读书笔记感兴趣的人。在信息流里，「自传」+「祛魅」比平淡的书名更容易停留。

**与原标题关系：** 保留「特斯拉 + 外星人」两条线，但点出读完传记后的结论。

### 候选 2

**标题：** 特斯拉59岁还能后空翻，这是人类还是外星人？

**为什么吸引人：** 具体画面（59岁、后空翻）比抽象讨论更有冲击力，疑问句促点击。适合猎奇向读者。

**与原标题关系：** 从正文最惊讶的细节切入，而非书名。

### 候选 3

**标题：** 《外星人访谈录》把我带进《特斯拉自传》，两本书读完后

**为什么吸引人：** 双书结构给出阅读路径，适合已关注读书账号的人。

**与原标题关系：** 直接对应原文叙事顺序。

## Sample CTA (reading theme)

- **cta_line1:** 读完《特斯拉自传》，我对《外星人访谈录》里「现在-成为者」的着迷，祛魅不少。

Reference output (after full pipeline): `scripts/xhs/output/articles/reading-category__post-13f67e2873/` — 7 PNGs for this article (page count is not a global target).

## Sample cover prompt

Soft warm paper texture, gentle reading-room light, sparse abstract book edges near the margins, low-contrast background, no readable text, no faces, no logos, no detailed object in the center or lower half, broad clean area for a large Chinese typography layer, 3:4 vertical composition.

## Sample post-caption.md

```markdown
# 小红书标题
读《特斯拉自传》后，我对外星人祛魅了

# 正文说明（可直接粘贴）
从《外星人访谈录》追到《特斯拉自传》，两个多小时读完，留下满屏的「厉害」。分享几条最让我惊讶的细节。

# 话题标签
#读书 #读书笔记 #特斯拉 #传记 #阅读记录
```
