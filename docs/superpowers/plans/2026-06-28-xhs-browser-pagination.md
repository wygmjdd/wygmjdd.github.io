# XHS Browser Pagination Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace estimate-first Xiaohongshu article body pagination with Chromium-measured pagination that prevents clipping and produces book-like page endings.

**Architecture:** Add a focused browser paginator module that owns one Playwright page per pagination run. `article.py` keeps parsing, cover rendering, body HTML rendering, and final filenames, but delegates body page selection to the browser paginator. Existing estimate paginator modules remain available for their existing tests and are removed from the default render path.

**Tech Stack:** Python 3, Playwright Chromium, pytest, existing `scripts.xhs.xhs_cards` modules.

**Spec:** `docs/superpowers/specs/2026-06-28-xhs-browser-pagination-design.md`

---

## File Structure

- Create `scripts/xhs/xhs_cards/article_browser_paginator.py`
  - Owns Chromium-measured pagination, input source normalization, fit checks, leading-piece splitting, page-ending cleanup, and final overflow verification.
- Create `scripts/xhs/tests/test_article_browser_paginator.py`
  - Tests browser paginator behavior directly with real `_render_body_page()` probes.
- Modify `scripts/xhs/xhs_cards/article.py`
  - Replaces the default `paginate_blocks()` / `balance_body_pages()` / `correct_body_page_*()` chain with `paginate_blocks_with_browser()`.
- Modify `scripts/xhs/tests/test_article_render.py`
  - Adds final render-path regression coverage for continuation indentation and no body overflow.

Keep all changes scoped to these files. Do not stage unrelated dirty files in the worktree.

---

### Task 1: Add Browser Paginator Tests

**Files:**
- Create: `scripts/xhs/tests/test_article_browser_paginator.py`

- [ ] **Step 1: Write failing tests for browser-measured pagination**

Create `scripts/xhs/tests/test_article_browser_paginator.py` with this content:

```python
from __future__ import annotations

from scripts.xhs.xhs_cards.article import _render_body_page
from scripts.xhs.xhs_cards.article_parser import ContentBlock
from scripts.xhs.xhs_cards.article_browser_paginator import (
    _BODY_FITS_JS,
    paginate_blocks_with_browser,
)


def _continues(all_pages: list[list[ContentBlock]], page_index: int, blocks: list[ContentBlock]) -> bool:
    if page_index <= 0 or not all_pages[page_index - 1] or not blocks:
        return False
    previous_last = all_pages[page_index - 1][-1]
    first_block = blocks[0]
    return (
        previous_last.kind == "paragraph"
        and first_block.kind == "paragraph"
        and previous_last.source_id == first_block.source_id
    )


def _render_probe(
    blocks: list[ContentBlock],
    total: int,
    page_index: int = 0,
    all_pages: list[list[ContentBlock]] | None = None,
) -> str:
    snapshot = all_pages if all_pages is not None else [blocks]
    return _render_body_page(
        "在我之外，还有一个安静看着我的我",
        blocks,
        page_index + 1,
        total,
        "我要改名叫嘟嘟",
        continues_paragraph=_continues(snapshot, page_index, blocks),
    )


def _joined(pages: list[list[ContentBlock]]) -> str:
    return "".join(block.text for page in pages for block in page)


def test_browser_paginator_preserves_text_and_assigns_source_ids() -> None:
    blocks = [
        ContentBlock("paragraph", "第一段第一句。第一段第二句。"),
        ContentBlock("paragraph", "第二段第一句。第二段第二句。"),
    ]

    pages = paginate_blocks_with_browser(blocks, _render_probe, max_chars=80)

    assert _joined(pages) == "".join(block.text for block in blocks)
    source_ids = [block.source_id for page in pages for block in page]
    assert set(source_ids) == {0, 1}


def test_browser_paginator_splits_leading_piece_before_opening_new_page() -> None:
    intro = "开头短句。"
    repeated = "我观察自己的情绪起伏，担忧焦虑证明我害怕失去某种东西，"
    long_paragraph = intro + repeated * 24 + "最后我终于慢慢平静下来。"
    blocks = [ContentBlock("paragraph", long_paragraph)]

    pages = paginate_blocks_with_browser(blocks, _render_probe, max_chars=80)

    assert len(pages) >= 2
    assert _joined(pages) == long_paragraph
    assert len("".join(block.text for block in pages[0])) > len(intro)


def test_browser_paginator_avoids_dangling_flow_punctuation_when_possible() -> None:
    repeated = "第一句提供背景，第二句继续展开，第三句承接前文，"
    blocks = [
        ContentBlock(
            "paragraph",
            repeated * 80 + "最后一句自然结束。",
        )
    ]

    pages = paginate_blocks_with_browser(blocks, _render_probe, max_chars=80)

    assert len(pages) >= 2
    for page in pages[:-1]:
        tail = page[-1].text.rstrip()
        assert tail[-1] not in "，,、；;：:"


def test_browser_paginator_final_pages_do_not_overflow() -> None:
    sentence = "这是一段足够长的中文句子，用来撑高真实浏览器分页并检查底部裁切。"
    blocks = [ContentBlock("paragraph", sentence * 40)]
    pages = paginate_blocks_with_browser(blocks, _render_probe, max_chars=80)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        browser_page = browser.new_page(viewport={"width": 1080, "height": 1440})
        try:
            for index, page in enumerate(pages):
                html = _render_probe(page, len(pages), index, pages)
                browser_page.set_content(html, wait_until="load")
                assert browser_page.evaluate(_BODY_FITS_JS), f"body page {index + 1} overflowed"
        finally:
            browser.close()
```

- [ ] **Step 2: Run the new test file and confirm it fails because the module does not exist**

Run:

```bash
python -m pytest scripts/xhs/tests/test_article_browser_paginator.py -q
```

Expected: FAIL during collection with `ModuleNotFoundError: No module named 'scripts.xhs.xhs_cards.article_browser_paginator'`.

- [ ] **Step 3: Commit the failing tests**

Run:

```bash
git add scripts/xhs/tests/test_article_browser_paginator.py
git commit -m "test: cover browser pagination behavior"
```

Expected: one commit containing only `scripts/xhs/tests/test_article_browser_paginator.py`.

---

### Task 2: Implement Browser-Measured Paginator

**Files:**
- Create: `scripts/xhs/xhs_cards/article_browser_paginator.py`

- [ ] **Step 1: Add the browser paginator implementation**

Create `scripts/xhs/xhs_cards/article_browser_paginator.py` with this content:

```python
"""Browser-measured pagination for Xiaohongshu article body slides."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scripts.xhs.xhs_cards.article_parser import ContentBlock
from scripts.xhs.xhs_cards.article_paginator import (
    _merge_adjacent_blocks,
    split_clauses,
    split_sentences,
)

_VIEWPORT: Any = {"width": 1080, "height": 1440}
_FLOW_END_PUNCT = "，,、；;：:"
_MIN_FRAGMENT_CHARS = 8
_CHAR_CHUNK = 28
_MAX_CLEANUP_PASSES = 3

_BODY_FITS_JS = """() => {
    const textArea = document.querySelector('.slide-article .article-body-text');
    if (!textArea) return false;
    return textArea.scrollHeight <= textArea.clientHeight + 1;
}"""

_CHROMIUM_INSTALL_HINT = (
    "Article browser pagination requires Playwright Chromium. "
    "Run `python -m playwright install chromium` from the repo root."
)


RenderPageHtml = Callable[[list[ContentBlock], int, int, list[list[ContentBlock]] | None], str]


def _clone(block: ContentBlock, text: str) -> ContentBlock:
    return ContentBlock(block.kind, text, block.source_id)


def _same_source(left: ContentBlock, right: ContentBlock) -> bool:
    return left.kind == right.kind and left.source_id == right.source_id


def _normalize_sources(blocks: list[ContentBlock]) -> list[ContentBlock]:
    return [
        ContentBlock(block.kind, block.text.strip(), index)
        for index, block in enumerate(blocks)
        if block.text.strip()
    ]


def _page_with_piece(page: list[ContentBlock], piece: ContentBlock) -> list[ContentBlock]:
    probe = list(page)
    if probe and _same_source(probe[-1], piece):
        probe[-1] = _clone(probe[-1], probe[-1].text + piece.text)
    else:
        probe.append(piece)
    return probe


def _snapshot_with_page(
    pages: list[list[ContentBlock]],
    page_index: int,
    candidate: list[ContentBlock],
) -> list[list[ContentBlock]]:
    snapshot = [list(page) for page in pages]
    if page_index < len(snapshot):
        snapshot[page_index] = candidate
    else:
        snapshot.append(candidate)
    return snapshot


def _page_fits(
    page: list[ContentBlock],
    page_index: int,
    pages: list[list[ContentBlock]],
    render_page_html: RenderPageHtml,
    browser_page: Any,
) -> bool:
    snapshot = _snapshot_with_page(pages, page_index, page)
    html = render_page_html(page, max(len(snapshot), 1), page_index, snapshot)
    browser_page.set_content(html, wait_until="load")
    return bool(browser_page.evaluate(_BODY_FITS_JS))


def _split_leading_chars(text: str) -> tuple[str, str] | None:
    stripped = text.strip()
    if len(stripped) <= _MIN_FRAGMENT_CHARS:
        return None
    end = min(len(stripped), _CHAR_CHUNK)
    if end < len(stripped):
        snap_at = -1
        for separator in "，,、；; ":
            index = stripped.rfind(separator, _MIN_FRAGMENT_CHARS, end)
            if index >= _MIN_FRAGMENT_CHARS:
                snap_at = max(snap_at, index + 1)
        if snap_at > _MIN_FRAGMENT_CHARS:
            end = snap_at
    return stripped[:end].strip(), stripped[end:].strip()


def _split_first_sentence(block: ContentBlock) -> tuple[ContentBlock, ContentBlock] | None:
    sentences = split_sentences(block.text)
    if len(sentences) <= 1:
        return None
    moved = sentences[0]
    remainder = "".join(sentences[1:]).strip()
    if not remainder:
        return None
    return _clone(block, moved), _clone(block, remainder)


def _split_first_clause(block: ContentBlock) -> tuple[ContentBlock, ContentBlock] | None:
    clauses = split_clauses(block.text)
    if len(clauses) <= 1:
        return None
    moved = clauses[0]
    remainder = "".join(clauses[1:]).strip()
    if not remainder:
        return None
    return _clone(block, moved), _clone(block, remainder)


def _split_first_chunk(block: ContentBlock) -> tuple[ContentBlock, ContentBlock] | None:
    split = _split_leading_chars(block.text)
    if split is None:
        return None
    moved, remainder = split
    if not moved or not remainder:
        return None
    return _clone(block, moved), _clone(block, remainder)


def _leading_splits(block: ContentBlock) -> list[tuple[ContentBlock, ContentBlock]]:
    splits: list[tuple[ContentBlock, ContentBlock]] = []
    for splitter in (_split_first_sentence, _split_first_clause, _split_first_chunk):
        split = splitter(block)
        if split is not None:
            moved, remainder = split
            if moved.text and remainder.text:
                splits.append(split)
    return splits


def _split_unit(block: ContentBlock) -> list[ContentBlock]:
    sentences = split_sentences(block.text)
    if len(sentences) > 1:
        return [_clone(block, sentence) for sentence in sentences if sentence.strip()]

    clauses = split_clauses(block.text)
    if len(clauses) > 1:
        return [_clone(block, clause) for clause in clauses if clause.strip()]

    chunks: list[ContentBlock] = []
    remainder = block
    while True:
        split = _split_first_chunk(remainder)
        if split is None:
            break
        moved, remainder = split
        chunks.append(moved)
    if remainder.text.strip():
        chunks.append(remainder)
    return chunks if len(chunks) > 1 else [block]


def _try_place_leading_piece(
    current: list[ContentBlock],
    unit: ContentBlock,
    pages: list[list[ContentBlock]],
    render_page_html: RenderPageHtml,
    browser_page: Any,
) -> tuple[list[ContentBlock], ContentBlock] | None:
    page_index = len(pages)
    for moved, remainder in _leading_splits(unit):
        candidate = _page_with_piece(current, moved)
        if _page_fits(candidate, page_index, pages, render_page_html, browser_page):
            return candidate, remainder
    return None


def _tail_is_bad(page: list[ContentBlock], next_page: list[ContentBlock]) -> bool:
    if not page or not next_page:
        return False
    last = page[-1]
    if last.kind != "paragraph":
        return False
    text = last.text.rstrip()
    if not text:
        return False
    if text[-1] in _FLOW_END_PUNCT:
        return True
    return (
        len(text) < _MIN_FRAGMENT_CHARS
        and next_page[0].kind == last.kind
        and next_page[0].source_id == last.source_id
    )


def _peel_trailing_piece(block: ContentBlock) -> tuple[ContentBlock | None, ContentBlock]:
    sentences = split_sentences(block.text)
    if len(sentences) > 1:
        remainder = "".join(sentences[:-1]).strip()
        moved = sentences[-1].strip()
        if remainder and moved:
            return _clone(block, remainder), _clone(block, moved)

    clauses = split_clauses(block.text)
    if len(clauses) > 1:
        remainder = "".join(clauses[:-1]).strip()
        moved = clauses[-1].strip()
        if remainder and moved:
            return _clone(block, remainder), _clone(block, moved)

    return None, block


def _prepend_piece(page: list[ContentBlock], piece: ContentBlock) -> list[ContentBlock]:
    if page and _same_source(piece, page[0]):
        return [_clone(piece, piece.text + page[0].text), *page[1:]]
    return [piece, *page]


def _cleanup_page_endings(
    pages: list[list[ContentBlock]],
    render_page_html: RenderPageHtml,
    browser_page: Any,
) -> list[list[ContentBlock]]:
    cleaned = [list(page) for page in pages if page]
    for _ in range(_MAX_CLEANUP_PASSES):
        changed = False
        for index in range(len(cleaned) - 1):
            page = cleaned[index]
            next_page = cleaned[index + 1]
            if not _tail_is_bad(page, next_page):
                continue

            remainder, moved = _peel_trailing_piece(page[-1])
            if remainder is None and len(page) <= 1:
                continue

            candidate_current = list(page[:-1])
            if remainder is not None:
                candidate_current.append(remainder)
            candidate_next = _prepend_piece(next_page, moved)

            snapshot = [list(p) for p in cleaned]
            snapshot[index] = candidate_current
            snapshot[index + 1] = candidate_next

            current_fits = _page_fits(
                candidate_current,
                index,
                snapshot,
                render_page_html,
                browser_page,
            )
            next_fits = _page_fits(
                candidate_next,
                index + 1,
                snapshot,
                render_page_html,
                browser_page,
            )
            if current_fits and next_fits:
                cleaned[index] = candidate_current
                cleaned[index + 1] = candidate_next
                changed = True
        if not changed:
            break
    return [page for page in cleaned if page]


def _verify_pages_fit(
    pages: list[list[ContentBlock]],
    render_page_html: RenderPageHtml,
    browser_page: Any,
) -> None:
    for index, page in enumerate(pages):
        if not _page_fits(page, index, pages, render_page_html, browser_page):
            preview = "".join(block.text for block in page)[:80]
            raise ValueError(f"Browser pagination produced overflowing body page {index + 1}: {preview}")


def paginate_blocks_with_browser(
    blocks: list[ContentBlock],
    render_page_html: RenderPageHtml,
    *,
    max_chars: int = 340,
) -> list[list[ContentBlock]]:
    """Paginate body blocks by asking Chromium whether each candidate page fits."""
    del max_chars

    normalized = _normalize_sources(blocks)
    if not normalized:
        return []

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Article browser pagination requires Playwright. "
            "Run `pip install -r scripts/requirements.txt` from the repo root."
        ) from exc

    pages: list[list[ContentBlock]] = []
    current: list[ContentBlock] = []
    queue = list(normalized)

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:
            if "Executable doesn't exist" in str(exc):
                raise RuntimeError(_CHROMIUM_INSTALL_HINT) from exc
            raise
        try:
            browser_page = browser.new_page(viewport=_VIEWPORT)
            while queue:
                unit = queue.pop(0)
                candidate = _page_with_piece(current, unit)
                if _page_fits(candidate, len(pages), pages, render_page_html, browser_page):
                    current = candidate
                    continue

                if current:
                    leading = _try_place_leading_piece(
                        current,
                        unit,
                        pages,
                        render_page_html,
                        browser_page,
                    )
                    if leading is not None:
                        current, remainder = leading
                        queue.insert(0, remainder)
                        continue

                    pages.append(_merge_adjacent_blocks(current))
                    current = []
                    queue.insert(0, unit)
                    continue

                split_units = _split_unit(unit)
                if len(split_units) <= 1:
                    preview = unit.text[:80]
                    raise ValueError(f"Text unit cannot fit on an empty body slide: {preview}")
                queue = split_units + queue

            if current:
                pages.append(_merge_adjacent_blocks(current))

            pages = _cleanup_page_endings(pages, render_page_html, browser_page)
            pages = [_merge_adjacent_blocks(page) for page in pages if page]
            _verify_pages_fit(pages, render_page_html, browser_page)
            browser_page.close()
        finally:
            browser.close()

    return pages
```

- [ ] **Step 2: Run browser paginator tests**

Run:

```bash
python -m pytest scripts/xhs/tests/test_article_browser_paginator.py -q
```

Expected: PASS for all tests in `test_article_browser_paginator.py`.

- [ ] **Step 3: Commit the browser paginator**

Run:

```bash
git add scripts/xhs/xhs_cards/article_browser_paginator.py
git commit -m "feat: add browser-measured article pagination"
```

Expected: one commit containing only `scripts/xhs/xhs_cards/article_browser_paginator.py`.

---

### Task 3: Wire Browser Paginator Into Article Rendering

**Files:**
- Modify: `scripts/xhs/xhs_cards/article.py`
- Modify: `scripts/xhs/tests/test_article_render.py`

- [ ] **Step 1: Write render-path regression tests**

Append these tests to `scripts/xhs/tests/test_article_render.py`:

```python

def test_render_article_slides_uses_browser_paginator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.xhs.xhs_cards import article as article_module
    from scripts.xhs.xhs_cards.article_parser import ContentBlock

    article_path = tmp_path / "article.md"
    article_path.write_text(
        "---\n"
        "title: 分页路径测试\n"
        "primary_category: summary\n"
        "---\n"
        "原始正文不应该直接进入 body。\n",
        encoding="utf-8",
    )
    cover_ai = tmp_path / COVER_AI_FILENAME
    cover_ai.write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "browser-path",
        "original_title": "分页路径测试",
        "xhs_title": "浏览器分页路径测试",
        "primary_category": "summary",
        "cover_ai": COVER_AI_FILENAME,
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    def fake_paginate(
        blocks: list[ContentBlock],
        render_page_html,
        *,
        max_chars: int,
    ) -> list[list[ContentBlock]]:
        assert max_chars == 120
        assert blocks[0].text == "原始正文不应该直接进入 body。"
        return [[ContentBlock("paragraph", "浏览器分页被调用。", 0)]]

    monkeypatch.setattr(article_module, "paginate_blocks_with_browser", fake_paginate)

    slides, _ = article_module.render_article_slides(manifest_path)
    body_html = slides[1][1]

    assert "浏览器分页被调用。" in body_html
    assert "原始正文不应该直接进入 body。" not in body_html


def test_render_article_slides_continues_long_paragraph_without_indent(tmp_path: Path) -> None:
    article_path = tmp_path / "article.md"
    sentence = "我观察自己的情绪起伏，担忧焦虑证明我害怕失去某种东西。"
    article_path.write_text(
        "---\n"
        "title: 长段落测试\n"
        "primary_category: summary\n"
        "---\n"
        f"{sentence * 48}\n",
        encoding="utf-8",
    )
    cover_ai = tmp_path / COVER_AI_FILENAME
    cover_ai.write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "long-paragraph",
        "original_title": "长段落测试",
        "xhs_title": "在我之外，还有一个安静看着我的我",
        "primary_category": "summary",
        "cover_ai": COVER_AI_FILENAME,
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    slides, _ = render_article_slides(manifest_path)
    body_slides = [
        (name, html)
        for name, html in slides
        if name != COVER_OUTPUT_FILENAME and not name.endswith("-end.png")
    ]

    assert len(body_slides) >= 2
    assert any("article-p-continue" in html for _, html in body_slides[1:])


def test_render_article_slides_browser_paginated_body_does_not_overflow(tmp_path: Path) -> None:
    article_path = tmp_path / "article.md"
    sentence = "这是一段足够长的中文句子，用来撑高真实浏览器分页并检查底部裁切。"
    article_path.write_text(
        "---\n"
        "title: 裁切测试\n"
        "primary_category: summary\n"
        "---\n"
        f"{sentence * 44}\n",
        encoding="utf-8",
    )
    cover_ai = tmp_path / COVER_AI_FILENAME
    cover_ai.write_bytes(b"\x89PNG\r\n\x1a\n")
    manifest = {
        "manifest_version": 1,
        "source": str(article_path),
        "slug": "overflow-check",
        "original_title": "裁切测试",
        "xhs_title": "在我之外，还有一个安静看着我的我",
        "primary_category": "summary",
        "cover_ai": COVER_AI_FILENAME,
        "cta_theme": "reading",
        "cta_line1": "共鸣句测试。",
        "nickname": "我要改名叫嘟嘟",
        "bio": "一个用文字分享生活和读书感悟的程序员",
        "chars_per_slide": 120,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    slides, _ = render_article_slides(manifest_path)
    body_slides = [
        (name, html)
        for name, html in slides
        if name != COVER_OUTPUT_FILENAME and not name.endswith("-end.png")
    ]

    from scripts.xhs.xhs_cards.article_browser_paginator import _BODY_FITS_JS
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        browser_page = browser.new_page(viewport={"width": 1080, "height": 1440})
        try:
            for name, html in body_slides:
                browser_page.set_content(html, wait_until="load")
                assert browser_page.evaluate(_BODY_FITS_JS), f"{name} overflowed"
        finally:
            browser.close()
```

- [ ] **Step 2: Run the render tests and confirm they fail before integration**

Run:

```bash
python -m pytest scripts/xhs/tests/test_article_render.py::test_render_article_slides_uses_browser_paginator scripts/xhs/tests/test_article_render.py::test_render_article_slides_continues_long_paragraph_without_indent scripts/xhs/tests/test_article_render.py::test_render_article_slides_browser_paginated_body_does_not_overflow -q
```

Expected: FAIL before integration. `test_render_article_slides_uses_browser_paginator` fails because `scripts.xhs.xhs_cards.article` does not yet expose `paginate_blocks_with_browser`.

- [ ] **Step 3: Wire `article.py` to the browser paginator**

In `scripts/xhs/xhs_cards/article.py`, replace the overflow-correction imports:

```python
from scripts.xhs.xhs_cards.article_overflow import (
    correct_body_page_overflows,
    correct_body_page_underfills,
)
from scripts.xhs.xhs_cards.article_paginator import (
    _merge_adjacent_blocks,
    balance_body_pages,
    paginate_blocks,
)
```

with:

```python
from scripts.xhs.xhs_cards.article_browser_paginator import paginate_blocks_with_browser
from scripts.xhs.xhs_cards.article_paginator import _merge_adjacent_blocks
```

Then replace the body page creation in `render_article_slides()`:

```python
    max_chars = int(manifest.get("chars_per_slide", 340))
    body_pages = paginate_blocks(article.blocks, max_chars)
    body_pages = balance_body_pages(body_pages)
```

with:

```python
    max_chars = int(manifest.get("chars_per_slide", 340))
```

After `_render_probe_page()` is defined, replace:

```python
    body_pages = correct_body_page_overflows(body_pages, _render_probe_page)
    body_pages = correct_body_page_underfills(body_pages, _render_probe_page)
    body_pages = [_merge_adjacent_blocks(page) for page in body_pages if page]
```

with:

```python
    body_pages = paginate_blocks_with_browser(
        article.blocks,
        _render_probe_page,
        max_chars=max_chars,
    )
    body_pages = [_merge_adjacent_blocks(page) for page in body_pages if page]
```

Keep `_page_continues_from_previous()` and `_render_probe_page()` unchanged, because the browser paginator passes the all-pages snapshot needed for continuation indentation.

- [ ] **Step 4: Run render tests again**

Run:

```bash
python -m pytest scripts/xhs/tests/test_article_render.py::test_render_article_slides_cover_body_end scripts/xhs/tests/test_article_render.py::test_render_article_slides_uses_browser_paginator scripts/xhs/tests/test_article_render.py::test_render_article_slides_continues_long_paragraph_without_indent scripts/xhs/tests/test_article_render.py::test_render_article_slides_browser_paginated_body_does_not_overflow -q
```

Expected: PASS for these four tests.

- [ ] **Step 5: Commit article integration**

Run:

```bash
git add scripts/xhs/xhs_cards/article.py scripts/xhs/tests/test_article_render.py
git commit -m "feat: use browser pagination for xhs articles"
```

Expected: one commit containing only `article.py` and `test_article_render.py`.

---

### Task 4: Run Focused Regression Suite

**Files:**
- No code changes unless a test failure reveals a defect in Task 2 or Task 3 files.

- [ ] **Step 1: Run browser and render tests together**

Run:

```bash
python -m pytest scripts/xhs/tests/test_article_browser_paginator.py scripts/xhs/tests/test_article_render.py -q
```

Expected: PASS.

- [ ] **Step 2: Run existing paginator tests to preserve old-module compatibility**

Run:

```bash
python -m pytest scripts/xhs/tests/test_article_paginator.py -q
```

Expected: PASS. If old estimate paginator tests fail because of import movement, restore compatibility without changing the new default render path.

- [ ] **Step 3: Run parser tests**

Run:

```bash
python -m pytest scripts/xhs/tests/test_article_parser.py -q
```

Expected: PASS.

- [ ] **Step 4: Commit any focused regression fixes**

If Tasks 4.1 through 4.3 pass without code changes, do not create a commit. If a defect required a fix, run:

```bash
git add scripts/xhs/xhs_cards/article_browser_paginator.py scripts/xhs/xhs_cards/article.py scripts/xhs/tests/test_article_browser_paginator.py scripts/xhs/tests/test_article_render.py
git commit -m "fix: stabilize browser pagination regressions"
```

Expected: one commit containing only the files changed for the regression fix.

---

### Task 5: Verify Actual Article Rendering

**Files:**
- No code changes unless render verification exposes a defect in Task 2 or Task 3 files.

- [ ] **Step 1: Run article QA if the sample manifest exists**

Run:

```bash
test -f scripts/xhs/output/articles/2025-nian-zhong-zong-jie-xia-ren-shi-zi-ji-hou-de-yi-ran-zuo-zi-ji/manifest.json && python -m scripts.xhs.generate_xhs_cards --series article --manifest scripts/xhs/output/articles/2025-nian-zhong-zong-jie-xia-ren-shi-zi-ji-hou-de-yi-ran-zuo-zi-ji/manifest.json --rerender --qa
```

Expected when the manifest exists: command exits 0 and prints generated PNG names plus QA output without `[error] overflow`.

Expected when the manifest is absent: command exits 0 with no output.

- [ ] **Step 2: Inspect generated body slide filenames if the sample render ran**

Run:

```bash
ls scripts/xhs/output/articles/2025-nian-zhong-zong-jie-xia-ren-shi-zi-ji-hou-de-yi-ran-zuo-zi-ji/*.png 2>/dev/null | sed -n '1,20p'
```

Expected: ordered PNG files beginning with `01-cover.png`, followed by body slides and one `*-end.png`.

- [ ] **Step 3: Run full xhs test directory**

Run:

```bash
python -m pytest scripts/xhs/tests -q
```

Expected: PASS.

- [ ] **Step 4: Commit any final verification fixes**

If verification required a code change, run:

```bash
git add scripts/xhs/xhs_cards/article_browser_paginator.py scripts/xhs/xhs_cards/article.py scripts/xhs/tests/test_article_browser_paginator.py scripts/xhs/tests/test_article_render.py
git commit -m "fix: verify browser pagination render path"
```

Expected: one commit containing only the verification fix files.

---

## Completion Checklist

- [ ] `scripts/xhs/xhs_cards/article_browser_paginator.py` exists and owns the new browser-measured pagination flow.
- [ ] `render_article_slides()` uses `paginate_blocks_with_browser()` as the default body-page path.
- [ ] Text completeness tests compare against parser-normalized block text.
- [ ] Final body slide tests verify Chromium sees no `.article-body-text` overflow.
- [ ] Continuation slides render `article-p-continue`.
- [ ] Non-final pages avoid dangling flow punctuation when cleanup can move the tail without overflow.
- [ ] Cover and end slide tests still pass.
- [ ] No unrelated dirty files are staged or committed.
