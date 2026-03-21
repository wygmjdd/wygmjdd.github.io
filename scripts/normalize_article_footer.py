#!/usr/bin/env python3
"""Normalize Hugo article bodies: inline source link; strip WeChat footer junk.

1. Moves the visual \"原文链接\" from the template into the last line of the main
   body (before any ↓↓↓ promo block), as small inline HTML.
2. Removes legacy \"↓↓↓…\" promo lines and any injected article-follow-cta HTML.

Idempotent: safe to run multiple times. Skips hub pages (list_category), section
_index.md files, and the homepage content tree outside content/docs if passed.

Usage:
  python scripts/normalize_article_footer.py
  python scripts/normalize_article_footer.py --dry-run
  python scripts/normalize_article_footer.py --root content/docs/2026/03
"""

from __future__ import annotations

import argparse
import re
import sys
from html import escape
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOCS = ROOT / "content" / "docs"

INLINE_LINK_MARKER = ">原文链接</a>）</small>"
_CTA_BLOCK_RE = re.compile(
    r'\n*<div class="article-follow-cta">.*?</div>\s*',
    re.DOTALL,
)

# Match lines that are only a horizontal rule / section divider (not article text).
_DIVIDER_LINE_RE = re.compile(r"^\s*\\?--+\s*$")
# Markdown horizontal rule: * * *, ***, etc.
_HR_LINE_RE = re.compile(r"^\s*(\*\s*){3,}\s*$")
# WeChat promo / footer line starting with arrows (with optional leading 【).
_PROMO_LINE_RE = re.compile(r"^\s*【?\s*↓↓↓")
_HR_WITH_INLINE_LINK_RE = re.compile(
    r"^(\*\s*\*\s*\*)\s+(<small>（<a href=\"[^\"]+\" rel=\"noopener noreferrer\">"
    r"原文链接</a>）</small>)\s*$",
    re.MULTILINE,
)


class MarkdownPost:
    __slots__ = ("metadata", "content")

    def __init__(self, metadata: dict[str, Any], content: str) -> None:
        self.metadata = metadata
        self.content = content


def parse_frontmatter_markdown(text: str) -> MarkdownPost:
    if text.startswith("\ufeff"):
        text = text[1:]
    stripped = text.lstrip("\n\r")
    if not stripped.startswith("---"):
        return MarkdownPost({}, text)

    lines = stripped.splitlines()
    if not lines or lines[0].strip() != "---":
        return MarkdownPost({}, text)

    end_idx: int | None = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return MarkdownPost({}, text)

    fm_block = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :])
    if body.startswith("\n"):
        body = body[1:]

    meta_raw = yaml.safe_load(fm_block)
    meta: dict[str, Any] = meta_raw if isinstance(meta_raw, dict) else {}
    return MarkdownPost(meta, body)


def dump_markdown(meta: dict[str, Any], body: str) -> str:
    fm = yaml.dump(
        meta,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip()
    return f"---\n{fm}\n---\n{body}"


def _last_content_line_index(lines: list[str]) -> int | None:
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        if not line.strip():
            continue
        if _DIVIDER_LINE_RE.match(line):
            continue
        if _HR_LINE_RE.match(line):
            continue
        return i
    return None


def append_source_link(main: str, source_url: str) -> str:
    if INLINE_LINK_MARKER in main:
        return main
    if not source_url.strip():
        return main

    href = escape(source_url.strip(), quote=True)
    suffix = (
        f' <small>（<a href="{href}" rel="noopener noreferrer">原文链接</a>）</small>'
    )

    lines = main.split("\n")
    idx = _last_content_line_index(lines)
    if idx is None:
        return main.rstrip() + suffix

    lines[idx] = lines[idx].rstrip() + suffix
    return "\n".join(lines).rstrip()


def strip_cta_html(body: str) -> str:
    """Remove legacy HTML CTA block injected by older versions of this script."""
    out = _CTA_BLOCK_RE.sub("\n", body)
    return out.rstrip("\n") + "\n"


def strip_legacy_follow_block(tail: str) -> str:
    """Remove promo lines at start of tail (↓↓↓…, with or without 欢迎关注)."""
    lines = tail.split("\n")
    out: list[str] = []
    skipping = True
    for line in lines:
        if skipping:
            if _PROMO_LINE_RE.match(line):
                continue
            if line.strip() == "":
                continue
            skipping = False
        out.append(line)
    return "\n".join(out).strip("\n")


def strip_trailing_promo_lines(body: str) -> str:
    """Remove orphan WeChat promo lines left after the HTML CTA block."""
    lines = body.split("\n")
    while lines:
        last = lines[-1]
        if not last.strip():
            lines.pop()
            continue
        if _PROMO_LINE_RE.match(last):
            lines.pop()
            continue
        break
    text = "\n".join(lines)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def repair_hr_attached_link(body: str) -> str:
    """Move inline 原文 link from '* * * <small>…' onto the previous paragraph."""
    changed = True
    while changed:
        changed = False
        m = _HR_WITH_INLINE_LINK_RE.search(body)
        if not m:
            break
        link = m.group(2)
        before = body[: m.start()].rstrip("\n")
        after = body[m.end() :].lstrip("\n")
        lines = before.split("\n") if before else []
        idx = _last_content_line_index(lines)
        if idx is None:
            break
        lines[idx] = lines[idx].rstrip() + " " + link
        new_before = "\n".join(lines)
        hr_line = m.group(1)
        if after:
            body = f"{new_before}\n\n{hr_line}\n\n{after}"
        else:
            body = f"{new_before}\n\n{hr_line}\n"
        changed = True
    return body


def repair_existing_body(body: str) -> str:
    body = strip_cta_html(body)
    body = repair_hr_attached_link(body)
    body = strip_trailing_promo_lines(body)
    return body


def transform_body(body: str, source_url: str | None) -> tuple[str, bool]:
    """Return (new_body, changed)."""
    idx = body.find("↓↓↓")
    if idx >= 0:
        main = body[:idx].rstrip()
        tail = body[idx:].strip()
    else:
        main = body.rstrip()
        tail = ""

    new_main = main
    if source_url:
        new_main = append_source_link(main, source_url)

    new_body = new_main
    if tail:
        cleaned_tail = strip_legacy_follow_block(tail)
        if cleaned_tail:
            new_body = f"{new_main}\n\n{cleaned_tail}"
        else:
            new_body = new_main
    elif source_url and INLINE_LINK_MARKER not in body:
        new_body = new_main

    return new_body, new_body != body


def should_skip(path: Path, meta: dict[str, Any]) -> str | None:
    if path.name == "_index.md":
        return "_index.md"
    if meta.get("list_category"):
        return "list_category hub"
    return None


def iter_targets(root: Path) -> list[Path]:
    return sorted(root.rglob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize article footers in Hugo content.")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_DOCS,
        help=f"Directory to scan (default: {DEFAULT_DOCS})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print changes only")
    args = parser.parse_args()
    root: Path = args.root.resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 1

    changed = 0
    skipped = 0
    for path in iter_targets(root):
        raw = path.read_text(encoding="utf-8")
        post = parse_frontmatter_markdown(raw)
        reason = should_skip(path, post.metadata)
        if reason:
            skipped += 1
            continue

        source_url = post.metadata.get("source_url")
        if not isinstance(source_url, str):
            source_url = None

        repaired = repair_existing_body(post.content)
        new_body, t_changed = transform_body(repaired, source_url)
        final_body = new_body if t_changed else repaired
        if final_body == post.content:
            skipped += 1
            continue

        new_text = dump_markdown(post.metadata, final_body)
        if new_text == raw:
            skipped += 1
            continue

        if args.dry_run:
            print(f"would update: {path.relative_to(ROOT)}")
        else:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            print(f"updated: {path.relative_to(ROOT)}")
        changed += 1

    print(f"Done. changed={changed}, skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
