#!/usr/bin/env python3
"""Convert WeChat-style inline image captions to figure/figcaption HTML.

Matches a whole line of the form::

    ![alt](/path/to/image.ext)Caption text

and replaces it with a Goldmark-safe HTML block using class ``figure-with-caption``
(see assets/_custom.scss). Lines that are only ``![alt](url)`` are left unchanged.

Examples::

    python3 scripts/postprocess_image_captions.py --dry-run
    python3 scripts/postprocess_image_captions.py
    python3 scripts/postprocess_image_captions.py content/docs/2026/01
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Whole line: image markdown immediately followed by caption (no blank line).
_LINE_IMG_CAPTION = re.compile(
    r"^!\[(?P<alt>[^\]]*)\]\((?P<url>[^)]+)\)\s*(?P<caption>\S.*)\s*$"
)


def line_to_figure(line_core: str) -> tuple[str, bool]:
    """If line_core matches image+caption, return HTML block; else original."""
    m = _LINE_IMG_CAPTION.match(line_core)
    if not m:
        return line_core, False
    alt = m.group("alt")
    url = m.group("url").strip()
    caption = m.group("caption").strip()
    if not caption:
        return line_core, False

    alt_attr = html.escape(alt, quote=True)
    src_attr = html.escape(url, quote=True)
    cap_html = html.escape(caption)
    block = (
        f'<figure class="figure-with-caption">\n'
        f'<img src="{src_attr}" alt="{alt_attr}" loading="lazy" decoding="async" />\n'
        f"<figcaption>{cap_html}</figcaption>\n"
        f"</figure>"
    )
    return block, True


def process_text(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    n = 0
    for line in lines:
        if line.endswith("\r\n"):
            core, nl = line[:-2], "\r\n"
        elif line.endswith("\n"):
            core, nl = line[:-1], "\n"
        else:
            core, nl = line, ""

        new_core, hit = line_to_figure(core)
        if hit:
            n += 1
        out.append(new_core + nl)
    return "".join(out), n


def iter_markdown_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix.lower() == ".md" else []
    return sorted(target.rglob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        default=[str(ROOT / "content" / "docs")],
        help="Files or directories of Markdown (default: content/docs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print counts only; do not write files",
    )
    args = parser.parse_args()

    total_hits = 0
    files_changed = 0

    for pstr in args.paths:
        target = Path(pstr)
        if not target.is_absolute():
            target = ROOT / target
        if not target.exists():
            print(f"Skip missing: {target}", file=sys.stderr)
            continue

        for md in iter_markdown_files(target):
            raw = md.read_text(encoding="utf-8")
            new, hits = process_text(raw)
            total_hits += hits
            if hits == 0:
                continue
            files_changed += 1
            rel = md.relative_to(ROOT)
            print(f"{rel}: {hits} line(s)")
            if not args.dry_run:
                md.write_text(new, encoding="utf-8")

    print(
        f"Done. {files_changed} file(s) with replacements, {total_hits} figure(s) total."
        + (" (dry-run)" if args.dry_run else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
