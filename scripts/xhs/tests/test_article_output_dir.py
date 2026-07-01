from __future__ import annotations

import json
from pathlib import Path

from scripts.xhs.xhs_cards.article_output_dir import (
    resolve_article_output_dir,
    title_to_pinyin_dir,
)


def test_title_to_pinyin_dir() -> None:
    assert title_to_pinyin_dir("特斯拉与外星人") == "te-si-la-yu-wai-xing-ren"


def test_title_to_pinyin_dir_empty() -> None:
    assert title_to_pinyin_dir("   ") == "untitled"


def test_resolve_output_dir_uses_pinyin_name(tmp_path: Path) -> None:
    articles_root = tmp_path / "articles"
    source = tmp_path / "content/docs/2026/06/yue-du-shu-mu__post-13f67e2873.md"
    source.parent.mkdir(parents=True)
    source.write_text("---\ntitle: x\n---\n", encoding="utf-8")

    name = resolve_article_output_dir(
        "特斯拉与外星人",
        source,
        articles_root=articles_root,
        repo_root=tmp_path,
    )
    assert name == "te-si-la-yu-wai-xing-ren"


def test_resolve_output_dir_reuses_same_source(tmp_path: Path) -> None:
    articles_root = tmp_path / "articles"
    dir_path = articles_root / "te-si-la-yu-wai-xing-ren"
    dir_path.mkdir(parents=True)
    source = tmp_path / "content/docs/2026/06/yue-du-shu-mu__post-13f67e2873.md"
    (dir_path / "manifest.json").write_text(
        json.dumps({"source": "content/docs/2026/06/yue-du-shu-mu__post-13f67e2873.md"}),
        encoding="utf-8",
    )

    name = resolve_article_output_dir(
        "特斯拉与外星人",
        source,
        articles_root=articles_root,
        repo_root=tmp_path,
    )
    assert name == "te-si-la-yu-wai-xing-ren"


def test_resolve_output_dir_disambiguates_collision(tmp_path: Path) -> None:
    articles_root = tmp_path / "articles"
    dir_path = articles_root / "te-si-la-yu-wai-xing-ren"
    dir_path.mkdir(parents=True)
    other_source = tmp_path / "content/docs/2026/06/yue-du-shu-mu__post-9999999999.md"
    (dir_path / "manifest.json").write_text(
        json.dumps({"source": "content/docs/2026/06/yue-du-shu-mu__post-9999999999.md"}),
        encoding="utf-8",
    )

    name = resolve_article_output_dir(
        "特斯拉与外星人",
        tmp_path / "content/docs/2026/06/yue-du-shu-mu__post-13f67e2873.md",
        articles_root=articles_root,
        repo_root=tmp_path,
    )
    assert name == "te-si-la-yu-wai-xing-ren-13f67e2873"
