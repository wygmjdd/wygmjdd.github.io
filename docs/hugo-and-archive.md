# Hugo 站点与本地归档

## 构建与部署

- 配置：`hugo.toml`，主题：`hugo-book`（Go module）
- 发布：`hugo --minify --gc --buildFuture`，产物在 `public/`（已 gitignore）
- GitHub Actions：`.github/workflows/hugo-gh-pages.yml`

## 文章与分类

- 正式内容：`content/`（首页为 `content/_index.md`，文章在 `content/docs/`）
- 分类 slug → 中文名：**`data/categories.yml`**（Hugo 模板与迁移脚本均读此文件，勿删）

## Jekyll 时代文件（本地归档）

迁移前的 `_posts`、`_rehydrated_posts`、`_data`、旧页面等放在 **`_archive/legacy-jekyll/`**。

- 该目录已加入 **`.gitignore`**，不会进 Git；换机器需自行拷贝或从旧提交恢复。
- 从归档生成 Hugo 内容：

  ```bash
  python3 -m scripts.wechat.migrate_jekyll_to_hugo_book
  ```

- 若目录不存在，上述脚本会报错；需先准备好归档目录或设置环境变量 `WYGMJDD_POSTS_DIR` 指向含 `.md` 的目录。

## 相关脚本

所有 `python3 -m scripts.wechat.*` 命令须在**仓库根目录**执行（Python 才能把 `scripts` 解析为包）。`update_manual` 的子进程已固定 `cwd` 为仓库根，从其他目录手跑单步命令时会 `ModuleNotFoundError`。

- `scripts/wechat/migrate_jekyll_to_hugo_book.py`：归档 → `content/docs/`
- `scripts/wechat/migrate.py` / `scripts/wechat/rehydrate_posts.py`：仍读写 `_archive/legacy-jekyll/` 下路径
- 完整流水线说明见 `docs/迁移脚本说明.md`
