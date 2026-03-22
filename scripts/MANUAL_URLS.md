# Manual article URL list (fallback when album parsing fails)

If `parse_album` fails for an album (e.g. WeChat page structure changed), you can provide article URLs manually.

## Format

Create a YAML file (e.g. `_archive/legacy-jekyll/_data/wechat_manual_article_urls.yml` or `scripts/manual_article_urls.yml`) keyed by **album slug** (same slug as in `_archive/legacy-jekyll/_data/wechat_albums.yml`). Each value is a list of article URLs.

Example:

```yaml
# Key = slug from wechat_albums.yml (e.g. 30min-diary, summary, reading-category)
30min-diary:
  - "https://mp.weixin.qq.com/s?__biz=..."
  - "https://mp.weixin.qq.com/s?__biz=..."
summary:
  - "https://mp.weixin.qq.com/s?__biz=..."
```

The migration script (Task 5) will read this file when album parsing is disabled or returns no URLs for an album, and use the listed URLs for that album's slug.
