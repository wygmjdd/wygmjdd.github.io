from __future__ import annotations

from pathlib import Path

import pytest

from scripts.wechat.migrate_jekyll_to_hugo_book import refuse_destructive_rebuild
from scripts.wechat.update_manual.__main__ import verify_rehydrated_outputs


def test_refuse_destructive_rebuild_when_source_too_small(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    docs = tmp_path / "content" / "docs"
    (docs / "2019" / "01").mkdir(parents=True)
    for i in range(60):
        (docs / "2019" / "01" / f"reading__post-{i}.md").write_text("# hi\n", encoding="utf-8")

    posts = tmp_path / "posts"
    posts.mkdir()
    (posts / "stub.md").write_text("---\ntitle: x\n---\n", encoding="utf-8")

    import scripts.wechat.migrate_jekyll_to_hugo_book as mod

    monkeypatch.setattr(mod, "OUT_DOCS", docs)
    monkeypatch.setattr(mod, "ROOT", tmp_path)

    with pytest.raises(SystemExit, match="Refusing full rebuild"):
        refuse_destructive_rebuild(posts, 1)


def test_verify_rehydrated_outputs_aborts_on_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stubs = tmp_path / "stubs"
    rehydrated = tmp_path / "rehydrated"
    stubs.mkdir()
    rehydrated.mkdir()
    stub = stubs / "2026-01-01-post-abc.md"
    stub.write_text("---\ntitle: t\n---\n", encoding="utf-8")

    import scripts.wechat.update_manual.__main__ as mod

    monkeypatch.setattr(mod, "REHYDRATED_DIR", rehydrated)

    with pytest.raises(SystemExit) as exc_info:
        verify_rehydrated_outputs([stub])
    assert exc_info.value.code == 2
