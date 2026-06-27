"""HTML renderers for Xiaohongshu series A (reading data overview)."""

from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any

_XHS_DIR = Path(__file__).resolve().parent.parent
_DATA_PATH = _XHS_DIR / "data" / "reading_inventory.json"
_CSS_PATH = Path(__file__).resolve().parent / "base.css"
_DEFAULT_BOOKS_PER_PAGE = 20


def load_inventory() -> dict[str, Any]:
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _css_block() -> str:
    return f"<style>{_CSS_PATH.read_text(encoding='utf-8')}</style>"


def _slide_shell(
    header: str,
    body: str,
    nickname: str,
    page: int,
    total: int,
) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  {_css_block()}
</head>
<body>
  <div class="slide">
    <div class="slide-header">{html.escape(header)}</div>
    <div class="slide-body">{body}</div>
    <div class="slide-footer">
      <span>@{html.escape(nickname)}</span>
      <span>{page}/{total}</span>
    </div>
  </div>
</body>
</html>"""


def _bar_chart_svg(yearly_posts: list[dict[str, Any]]) -> str:
    max_count = max(item["count"] for item in yearly_posts)
    chart_w, chart_h = 880, 520
    bar_gap = 28
    bar_w = (chart_w - bar_gap * (len(yearly_posts) - 1)) / len(yearly_posts)
    bars: list[str] = []
    labels: list[str] = []

    for index, item in enumerate(yearly_posts):
        height = 40 if max_count == 0 else max(40, (item["count"] / max_count) * 420)
        x = index * (bar_w + bar_gap)
        y = chart_h - height - 60
        highlight = item["year"] == "2023"
        fill = "#c45c4a" if highlight else "#d4c4b0"
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{height:.1f}" '
            f'rx="8" fill="{fill}" />'
        )
        count_fill = "#c45c4a" if highlight else "#6b635a"
        bars.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{y - 14}" text-anchor="middle" '
            f'font-size="26" fill="{count_fill}" font-weight="700">{item["count"]}篇</text>'
        )
        labels.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{chart_h - 20}" text-anchor="middle" '
            f'font-size="28" fill="#6b635a">{item["year"][-2:]}年</text>'
        )

    return (
        f'<svg width="{chart_w}" height="{chart_h}" viewBox="0 0 {chart_w} {chart_h}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'{"".join(bars)}{"".join(labels)}</svg>'
    )


def _donut_chart_svg(categories: list[dict[str, Any]], total: int) -> str:
    size = 360
    cx, cy, outer_r, inner_r = size / 2, size / 2, 150, 88
    start_angle = -math.pi / 2
    slices: list[str] = []

    for item in categories:
        fraction = item["value"] / total
        sweep = fraction * 2 * math.pi
        end_angle = start_angle + sweep
        x1 = cx + outer_r * math.cos(start_angle)
        y1 = cy + outer_r * math.sin(start_angle)
        x2 = cx + outer_r * math.cos(end_angle)
        y2 = cy + outer_r * math.sin(end_angle)
        xi1 = cx + inner_r * math.cos(end_angle)
        yi1 = cy + inner_r * math.sin(end_angle)
        xi2 = cx + inner_r * math.cos(start_angle)
        yi2 = cy + inner_r * math.sin(start_angle)
        large_arc = 1 if sweep > math.pi else 0
        slices.append(
            f'<path d="M {x1:.2f} {y1:.2f} A {outer_r} {outer_r} 0 {large_arc} 1 {x2:.2f} {y2:.2f} '
            f'L {xi1:.2f} {yi1:.2f} A {inner_r} {inner_r} 0 {large_arc} 0 {xi2:.2f} {yi2:.2f} Z" '
            f'fill="{item["color"]}" />'
        )
        start_angle = end_angle

    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'{"".join(slices)}'
        f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="52" font-weight="700" '
        f'fill="#2c2c2c">{total}</text>'
        f'<text x="{cx}" y="{cy + 30}" text-anchor="middle" font-size="24" fill="#8a7f72">本</text>'
        f"</svg>"
    )


def _legend_html(categories: list[dict[str, Any]]) -> str:
    items = []
    for item in categories:
        items.append(
            f'<div class="legend-item">'
            f'<span class="legend-dot" style="background:{item["color"]}"></span>'
            f'<span>{html.escape(item["label"])}</span>'
            f'<span class="legend-value">{item["value"]}本</span>'
            f"</div>"
        )
    return f'<div class="legend">{"".join(items)}</div>'


def _card_list(items: list[dict[str, str]]) -> str:
    cards = []
    for item in items:
        cards.append(
            f'<div class="info-card">'
            f'<div class="info-card-title">{html.escape(item["title"])}</div>'
            f'<div class="info-card-desc">{html.escape(item["desc"])}</div>'
            f"</div>"
        )
    return f'<div class="card-list">{"".join(cards)}</div>'


def _book_title_display(book: str) -> str:
    if book.startswith("《") and book.endswith("》"):
        return book
    return f"《{book}》"


def _book_chip(book: str) -> str:
    display = _book_title_display(book)
    return f'<span class="book-chip">{html.escape(display)}</span>'


def _categories_by_id(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {category["id"]: category for category in inventory["categories"]}


def _category_section(category: dict[str, Any], *, compact: bool) -> str:
    header_class = "book-list-header book-list-header-compact" if compact else "book-list-header"
    grid_class = "book-grid book-grid-dense" if compact else "book-grid"
    chips = "".join(_book_chip(book) for book in category["books"])
    return f"""
      <div class="book-section">
        <div class="{header_class}">
          <span class="book-list-dot" style="background:{category["color"]}"></span>
          <span class="book-list-title">{html.escape(category["title"])}</span>
          <span class="book-list-count">{category["count"]}本</span>
        </div>
        <div class="{grid_class}">{chips}</div>
      </div>
    """


def _merged_book_slide_body(categories: list[dict[str, Any]]) -> str:
    book_total = sum(category["count"] for category in categories)
    multi_section = len(categories) > 1
    compact = multi_section or book_total >= 40
    dense = multi_section and book_total >= 24
    wrapper_class = "book-slide-dense" if dense else ""
    sections = "".join(_category_section(category, compact=compact) for category in categories)
    if wrapper_class:
        return f'<div class="{wrapper_class}">{sections}</div>'
    return sections


def _overview_slide_specs(inventory: dict[str, Any]) -> list[tuple[str, str]]:
    summary = inventory["summary"]
    specs: list[tuple[str, str]] = []

    cover_body = f"""
      <div class="title-xl">6年读完<br/><span class="accent">{summary["finished_books"]}本</span></div>
      <div class="subtitle">我的阅读结构，全公开</div>
      <div class="stat-row">
        <div class="stat-card">
          <div class="stat-value">{summary["post_count"]}</div>
          <div class="stat-label">篇读书笔记</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{summary["span"]}</div>
          <div class="stat-label">阅读跨度</div>
        </div>
      </div>
      <div class="hook-box">每读完一本写一篇笔记<br/>这是我能坚持下来的「养成游戏」</div>
    """
    specs.append(("01-cover.png", cover_body))

    yearly_body = f"""
      <div class="title-md">年度笔记数量</div>
      <div class="section-label">阅读书目发文篇数 · 单位：篇</div>
      <div class="chart-wrap">{_bar_chart_svg(inventory["yearly_posts"])}</div>
      <div class="chart-caption">
        <span class="accent">2023 年最多，41 篇</span> · 那一年阅读习惯彻底稳住了
      </div>
    """
    specs.append(("02-yearly.png", yearly_body))

    category_total = sum(item["value"] for item in inventory["category_share"])
    category_body = f"""
      <div class="title-md">类别占比</div>
      <div class="section-label">按阅读书目归类 · 共 {category_total} 本</div>
      <div class="chart-wrap">{_donut_chart_svg(inventory["category_share"], category_total)}</div>
      {_legend_html(inventory["category_share"])}
      <div class="chart-caption" style="margin-top:20px">文学最多（44本），心理 23 本次之，技术 22 本</div>
    """
    specs.append(("03-category.png", category_body))

    taxonomy_body = f"""
      <div class="title-md">我的分类体系</div>
      <div class="two-col">
        <div class="col-card">
          <h3>四大主轴（2024.11）</h3>
          {_card_list(inventory["four_axes"])}
        </div>
        <div class="col-card">
          <h3>三类书（2024.05）</h3>
          {_card_list(inventory["three_book_types"])}
        </div>
      </div>
    """
    specs.append(("04-taxonomy.png", taxonomy_body))

    scene_items = []
    for index, scene in enumerate(inventory["reading_scenes"], start=1):
        scene_items.append(
            f'<div class="scene-item">'
            f'<span class="scene-num">{index}</span>'
            f"<span>{html.escape(scene)}</span>"
            f"</div>"
        )
    scenes_body = f"""
      <div class="title-md">阅读场景</div>
      <div class="section-label">2025–2026 · 把阅读嵌进日常动线</div>
      <div class="scene-list">{"".join(scene_items)}</div>
    """
    specs.append(("05-scenes.png", scenes_body))

    return specs


def _resolve_display_categories(group: dict[str, Any], category_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    if "sections" in group:
        display_categories: list[dict[str, Any]] = []
        for section in group["sections"]:
            books: list[str] = []
            for category_id in section["category_ids"]:
                books.extend(category_map[category_id]["books"])
            display_categories.append(
                {
                    "title": section["title"],
                    "color": section["color"],
                    "count": len(books),
                    "books": books,
                }
            )
        return display_categories

    return [category_map[category_id] for category_id in group["category_ids"]]


def _book_slide_specs(inventory: dict[str, Any]) -> list[tuple[str, str]]:
    category_map = _categories_by_id(inventory)
    groups = inventory.get("book_slide_groups")
    if not groups:
        groups = [{"id": category["id"], "category_ids": [category["id"]]} for category in inventory["categories"]]

    specs: list[tuple[str, str]] = []
    for index, group in enumerate(groups, start=6):
        categories = _resolve_display_categories(group, category_map)
        filename = f"{index:02d}-books-{group['id']}.png"
        body = _merged_book_slide_body(categories)
        specs.append((filename, body))

    return specs


def render_series_a_slides(data: dict[str, Any] | None = None) -> list[tuple[str, str]]:
    """Return (filename, html) pairs for series A."""
    inventory = data or load_inventory()
    meta = inventory["meta"]
    header = meta["series_title"]
    nickname = meta["nickname"]

    body_specs = _overview_slide_specs(inventory) + _book_slide_specs(inventory)
    total = len(body_specs)

    return [
        (filename, _slide_shell(header, body, nickname, page, total))
        for page, (filename, body) in enumerate(body_specs, start=1)
    ]
