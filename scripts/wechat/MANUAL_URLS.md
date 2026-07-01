# Manual article URL list (fallback when album parsing fails)

If `parse_album` fails for an album (e.g. WeChat page structure changed), you can provide article URLs manually.

## Format

Create a YAML file (e.g. `_archive/legacy-jekyll/_data/wechat_manual_article_urls.yml` or `scripts/wechat/manual_article_urls.yml`) keyed by **album slug** (same slug as in `_archive/legacy-jekyll/_data/wechat_albums.yml`). Each value is a list of article URLs.

Example:

```yaml
# Key = category slug from data/categories.yml (e.g. 30-fen-zhong-ri-ji, zong-jie, yue-du-shu-mu)
30-fen-zhong-ri-ji:
  - "https://mp.weixin.qq.com/s?__biz=..."
  - "https://mp.weixin.qq.com/s?__biz=..."
summary:
  - "https://mp.weixin.qq.com/s?__biz=..."
```

The migration script (Task 5) will read this file when album parsing is disabled or returns no URLs for an album, and use the listed URLs for that album's slug.
