# 公众号文章搬运与 Pages 标签 — 设计文档

**日期**: 2026-03-14

## 目标

1. **搬运**：从公众号专辑链接批量抓取文章（约 500 篇存量），保留 Markdown 格式，保存为 Jekyll 可用的 `_posts`。
2. **搬运后**：在站点内提供两类入口：
   - **时间标签**：按年、按月浏览（如 `/archive/` → 某年 → 某月 → 该月文章列表）。
   - **类型标签**：按专辑/类型浏览（如「阅读书目」→ 该类型下所有文章）；类型页 URL 使用英文或拼音，页面展示仍用中文名称。

## 配置格式

- 文件：`_data/wechat_albums.yml`（或项目内约定的 config 路径）。
- 结构：专辑列表，每项包含 `name`（中文）、`url`（专辑页链接）、`slug`（可选，用于 URL）。

```yaml
albums:
  - name: "三十分钟日记"
    slug: "30min-diary"          # 可选；不填则用 name 的拼音
    url: "https://mp.weixin.qq.com/mp/appmsgalbum?..."
  - name: "年终总结"
    slug: "year-end-summary"
    url: "https://mp.weixin.qq.com/mp/appmsgalbum?..."
  - name: "阅读书目"
    # 无 slug → 脚本用 pinyin 生成，如 yuedushumu
    url: "https://mp.weixin.qq.com/mp/appmsgalbum?..."
```

- 类型页 URL：使用 `slug`（有则用，无则用拼音），避免 URL 中出现中文，便于兼容性与分享。
- 页面展示名称：仍用中文 `name`，通过 `_data/categories.yml`（slug → 中文名）在模板中显示。

## 搬运脚本

- **输入**：上述 YAML 配置（可支持后续追加专辑）。
- **专辑页解析**：优先用 Playwright 从专辑页解析文章链接；若某专辑解析失败，支持 fallback：你提供该专辑下的文章 URL 列表（如单独 YAML 或 CSV），脚本只做「按 URL 抓正文 + 打标签」。
- **去重与标签**：按文章 URL 去重；一篇文章出现在多个专辑则打多个类型标签（front matter 中 `categories` 为多个 slug）。
- **单篇抓取**：请求文章页 → 提取正文（如 `#js_content`）与发布日期 → HTML 转 Markdown（如 html2text）→ 写入 `_posts/YYYY-MM-DD-slug.md`。
- **Front matter**：至少包含 `title`、`date`、`categories: [slug1, slug2, ...]`、`source_url`；日期取不到时用抓取日。
- **规模与稳健**：约 500 篇；请求间延时（如 2–5 秒）、断点续跑（已抓 URL 跳过），可分批执行。

## 站点结构（搬运之后）

- **文章**：全部放在 `_posts/`，使用 Jekyll 标准 `date` 与 `categories`（categories 存 slug，便于生成英文/拼音 URL）。
- **类型展示名**：`_data/categories.yml` 维护 `slug → 中文名`，供模板显示「阅读书目」「年终总结」等。
- **时间标签**
  - 入口：`/archive/`（或 `/pages/by-date/`）。
  - 层级：年 → 月 → 文章列表；URL 形如 `/archive/`、`/archive/2024/`、`/archive/2024/03/`。
  - 实现：Liquid 对 `site.posts` 按 `date | date: "%Y"` 与 `date | date: "%Y-%m"` 分组。
- **类型标签**
  - 总览：列出所有类型（从 `site.categories` 或 `_data/categories.yml`），每项链接到对应类型合集页。
  - 合集页 URL：`/category/<slug>/`（如 `/category/year-end-summary/`、`/category/yuedushumu/`）。
  - 页面标题/展示：用 `_data/categories.yml` 中的中文名（如「年终总结」）。

## 边界与约定

- 同一文章在多专辑：只生成一篇 `_posts` 文件，`categories` 包含多个 slug。
- 专辑解析失败：可对该专辑改为手动提供文章 URL 列表，脚本仅负责抓正文并打上该专辑的 slug。
- 类型 URL 一律用英文或拼音（slug），不在 URL 中使用汉字；展示名保持中文。

---

*设计确认后，实现计划见同目录下 implementation 文档。*
