#!/usr/bin/env python3
"""Generate Xiaohongshu card images via Playwright."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from scripts.xhs.xhs_cards.article import render_article_slides
from scripts.xhs.xhs_cards.series_6years import render_6years_infographic_html
from scripts.xhs.xhs_cards.series_a import render_series_a_slides

_XHS_DIR = Path(__file__).resolve().parent
_DEFAULT_OUTPUT = _XHS_DIR / "output" / "series-a"
_DEFAULT_6YEARS_OUTPUT = _XHS_DIR / "output" / "6-years-updating.png"
_VIEWPORT = {"width": 1080, "height": 1440}


def _launch_browser(playwright: Any) -> Any:
    try:
        return playwright.chromium.launch(headless=True)
    except Exception:
        return playwright.chromium.launch(headless=True, channel="chrome")


def _screenshot_slides(slides: list[tuple[str, str]], output_dir: Path) -> list[Path]:
    from playwright.sync_api import sync_playwright

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    with sync_playwright() as playwright:
        browser = _launch_browser(playwright)
        try:
            page = browser.new_page(viewport=_VIEWPORT, device_scale_factor=2)
            page.set_default_timeout(60_000)
            for filename, slide_html in slides:
                out_path = output_dir / filename
                page.set_content(slide_html, wait_until="load")
                page.screenshot(path=str(out_path), full_page=False, timeout=60_000)
                written.append(out_path)
        finally:
            browser.close()

    return written


def _screenshot_infographic(slide_html: str, output_path: Path) -> Path:
    from playwright.sync_api import sync_playwright

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = _launch_browser(playwright)
        try:
            page = browser.new_page(viewport={"width": 1080, "height": 1440}, device_scale_factor=2)
            page.set_default_timeout(60_000)
            page.set_content(slide_html, wait_until="load")
            height = page.evaluate("() => document.documentElement.scrollHeight")
            page.set_viewport_size({"width": 1080, "height": height})
            page.screenshot(path=str(output_path), full_page=True, timeout=60_000)
        finally:
            browser.close()

    return output_path


def _run_article_series(manifest_path: Path, rerender: bool) -> None:
    manifest_path = manifest_path.resolve()
    if not manifest_path.is_file():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    if rerender:
        print(f"Re-rendering from manifest: {manifest_path}", flush=True)

    slides, output_dir = render_article_slides(manifest_path)
    paths = _screenshot_slides(slides, output_dir)
    print(f"Generated {len(paths)} images in {output_dir}")
    for path in paths:
        print(f"  {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Xiaohongshu card images.")
    parser.add_argument(
        "--series",
        choices=["a", "6years", "article"],
        default="a",
        help="Card series to generate (default: a)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory for series a, or output file path for series 6years",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to manifest.json (required for --series article)",
    )
    parser.add_argument(
        "--rerender",
        action="store_true",
        help="Regenerate PNGs from existing manifest and cover-bg.png (article series only)",
    )
    args = parser.parse_args()

    if args.series == "article":
        if args.manifest is None:
            print("ERROR: --series article requires --manifest", file=sys.stderr)
            raise SystemExit(2)
        _run_article_series(args.manifest, args.rerender)
        return

    if args.series == "a":
        output_dir = (args.output or _DEFAULT_OUTPUT).resolve()
        slides = render_series_a_slides()
        paths = _screenshot_slides(slides, output_dir)
        print(f"Generated {len(paths)} images in {output_dir}")
        for path in paths:
            print(f"  {path.name}")
        return

    if args.series == "6years":
        output_path = (args.output or _DEFAULT_6YEARS_OUTPUT).resolve()
        path = _screenshot_infographic(render_6years_infographic_html(), output_path)
        print(f"Generated infographic: {path}")
        return

    raise SystemExit(f"Unsupported series: {args.series}")


if __name__ == "__main__":
    main()
