from __future__ import annotations

from pathlib import Path

import yaml


def article_path_by_title(title: str, docs_root: Path = Path("content/docs")) -> Path:
    matches: list[Path] = []
    for path in sorted(docs_root.rglob("*.md")):
        if path.name == "_index.md" or "hubs" in path.parts:
            continue

        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue

        end = text.find("\n---\n", 4)
        if end < 0:
            continue

        frontmatter = yaml.safe_load(text[4:end])
        if isinstance(frontmatter, dict) and frontmatter.get("title") == title:
            matches.append(path)

    if len(matches) != 1:
        raise AssertionError(f"expected one article titled {title!r}, found {matches}")
    return matches[0]
