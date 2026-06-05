# 文末「原文链接」添加更新日期

## 背景

每篇文章末尾有内联 HTML 形式的「原文链接」，当前格式为：

```html
<small>（<a href="..." rel="noopener noreferrer">原文链接</a>）</small>
```

目标是在链接后追加发布日期，格式为：

```html
<small>（<a href="..." rel="noopener noreferrer">原文链接</a>，更新于2019-06-15。）</small>
```

日期取自 frontmatter 的 `date` 字段（如 `date: '2019-06-15'`），格式固定为 `YYYY-MM-DD`。仅「原文链接」为可点击链接，「，更新于…。」为普通文本。

## 现状

- 链接由 `scripts/normalize_article_footer.py` 的 `append_source_link()` 写入正文，非 Hugo 模板渲染。
- `content/docs/` 下约 300+ 篇文章已是旧格式。
- 迁移流水线（含 `update_manual`）在 Step 4 会调用该脚本。
- Hugo `layouts/_default/single.html` 直接输出 `.Content`，不涉及文末链接。

## 方案

采用**方案 A：改脚本 + 批量更新**，与现有流水线保持一致。

不改 Hugo 模板，不改其他迁移脚本。

## 改动范围

仅修改 `scripts/normalize_article_footer.py`，新增测试文件 `scripts/test_normalize_article_footer.py`。

批量执行脚本更新全部已有文章：

```bash
python3 scripts/normalize_article_footer.py --dry-run
python3 scripts/normalize_article_footer.py
```

## 实现细节

### 日期解析

从 frontmatter `date` 读取，兼容：

- 字符串：`'2019-06-15'`
- YAML 解析后的 `datetime.date` / `datetime.datetime`

统一输出 `YYYY-MM-DD`。解析失败时不追加日期部分，仅保留链接。

### 链接块正则

匹配文末已有的原文链接块：

```regex
 <small>（<a href="([^"]+)" rel="noopener noreferrer">原文链接</a>(?:，更新于\d{4}-\d{2}-\d{2}。)?）</small>
```

### 核心函数

| 函数 | 职责 |
|------|------|
| `format_date_from_meta(meta)` | 从 metadata 提取 `YYYY-MM-DD` 字符串 |
| `build_source_link_suffix(href, date_str)` | 生成完整 `<small>…</small>` 后缀 |
| `normalize_source_link(body, source_url, date_str)` | 追加、升级或跳过链接块 |
| `transform_body()` | 传入 metadata 中的 date |
| `main()` | 将 `post.metadata` 传入 transform 链路 |

移除或替换现有的 `INLINE_LINK_MARKER` 简单存在性检查，改为基于正则的精确比对。

### 幂等行为

| 情况 | 行为 |
|------|------|
| 已有链接，href 和日期均正确 | 跳过（`changed=False`） |
| 已有链接，缺日期（旧格式） | 升级，补上 `，更新于{date}。` |
| 已有链接，日期与 frontmatter 不一致 | 更新日期 |
| 无链接，有 `source_url` | 追加新格式 |
| 无链接，无 `source_url` | 跳过 |
| 有链接，无 `date` | 保留链接，不加日期部分 |
| hub 页（`list_category`）/ `_index.md` | 跳过（保持现有逻辑） |

多次执行 `normalize_article_footer.py` 结果不变。

### `repair_hr_attached_link` 兼容

更新 `_HR_WITH_INLINE_LINK_RE` 正则，使其同时匹配带日期和不带日期的链接块，修复逻辑保持不变。

## 测试

`scripts/test_normalize_article_footer.py` 覆盖：

1. 新文章追加（有 date）
2. 新文章追加（无 date，仅链接无日期后缀）
3. 旧格式升级为新格式
4. 已是新格式 → 二次执行不变（幂等）
5. frontmatter `date` 变更后日期同步更新
6. 无 `source_url` 不追加链接
7. `format_date_from_meta` 对字符串和 datetime 的解析

## 不在范围内

- Hugo 模板或 render hook 方案
- 修改 `docs/迁移脚本说明.md`（脚本用法不变，仅输出格式变化）
- 引入独立的 `last_updated` frontmatter 字段

## 验收标准

1. 示例文章 `content/docs/2019/06/life-diary__post-c66e255f30.md` 文末显示 `（原文链接，更新于2019-06-15。）`
2. 全部 `content/docs/` 文章批量更新完成
3. 脚本可重复执行且无文件变更（幂等）
4. 测试全部通过
5. `update_manual` 流水线中新导入文章自动获得新格式
