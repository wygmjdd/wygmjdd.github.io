from __future__ import annotations

from pathlib import Path

from scripts.xhs.xhs_cards.article_layout import AVAILABLE_TEXT_HEIGHT, EFFECTIVE_TEXT_HEIGHT, page_content_height
from scripts.xhs.xhs_cards.article_parser import ContentBlock, parse_article_file
from scripts.xhs.xhs_cards.article_paginator import (
    _merge_adjacent_blocks,
    char_count,
    hard_split_text,
    paginate_blocks,
    split_block_to_chunks,
    split_clauses,
    split_sentences,
)


def test_split_sentences() -> None:
    text = "第一句。第二句！第三句？"
    assert split_sentences(text) == ["第一句。", "第二句！", "第三句？"]


def test_split_sentences_respects_parentheses() -> None:
    text = "前言。（括号里还有一句。仍然在同一句。）后文。"
    assert split_sentences(text) == ["前言。", "（括号里还有一句。仍然在同一句。）后文。"]


def test_split_clauses() -> None:
    text = "我喜欢工作，也喜欢同事，这是整句。"
    assert split_clauses(text) == ["我喜欢工作，", "也喜欢同事，", "这是整句。"]


def test_split_clauses_respects_parentheses() -> None:
    text = "前言，（括号里，还有逗号）后文。"
    assert split_clauses(text) == ["前言，", "（括号里，还有逗号）后文。"]


def test_paginate_no_lone_closing_paren() -> None:
    article = parse_article_file(Path("content/docs/2026/06/reading-category__post-13f67e2873.md"))
    pages = paginate_blocks(article.blocks, max_chars=340)
    for page in pages:
        for block in page:
            stripped = block.text.strip()
            assert stripped not in {"）", "）。"}
            assert not (stripped.startswith("）") and char_count(stripped) < 8)


def test_hard_split_text() -> None:
    text = "a" * 250
    parts = hard_split_text(text, 100)
    assert len(parts) == 3
    assert all(char_count(part) <= 100 for part in parts)
    assert "".join(parts) == text


def test_split_block_splits_oversized_sentence() -> None:
    sentence = "长" * 250 + "。"
    block = ContentBlock("paragraph", sentence)
    chunks = split_block_to_chunks(block, 200)
    assert len(chunks) > 1
    assert all(char_count(chunk.text) <= 200 for chunk in chunks)


def test_paginate_keeps_short_blocks_together() -> None:
    blocks = [
        ContentBlock("paragraph", "短段一。"),
        ContentBlock("quote", "引用块。"),
        ContentBlock("paragraph", "短段二。"),
    ]
    pages = paginate_blocks(blocks, max_chars=200)
    assert len(pages) == 1
    assert len(pages[0]) == 3


def test_paginate_splits_when_block_exceeds_slide_height() -> None:
    from scripts.xhs.xhs_cards.article_layout import AVAILABLE_TEXT_HEIGHT, EFFECTIVE_TEXT_HEIGHT, page_content_height

    sentence = "这是一段足够长的中文句子，用于撑高分页估算。" * 3
    long_text = (sentence + "。") * 80
    blocks = [ContentBlock("paragraph", long_text)]
    pages = paginate_blocks(blocks, max_chars=200)
    assert len(pages) >= 2
    for page in pages:
        assert page_content_height(page) <= EFFECTIVE_TEXT_HEIGHT + 1


def test_paragraph_can_continue_on_next_slide() -> None:
    sentence = "这是一段足够长的中文句子，用来撑高分页估算和跨页连续阅读体验。"
    long_paragraph = "".join(sentence for _ in range(40))
    blocks = [ContentBlock("paragraph", long_paragraph)]
    pages = paginate_blocks(blocks, max_chars=200)
    assert len(pages) >= 2
    joined = "".join(block.text for page in pages for block in page)
    assert joined == long_paragraph
    assert any("用来撑高分页估算" in block.text for block in pages[0])
    assert any(sentence in block.text for page in pages for block in page)


def test_paginate_fills_first_slide_before_starting_second() -> None:
    article = parse_article_file(Path("content/docs/2026/06/reading-category__post-13f67e2873.md"))
    pages = paginate_blocks(article.blocks, max_chars=340)
    first_page = pages[0]
    first_page_text = "".join(block.text for block in first_page)

    assert "《外星人访谈录》" in first_page_text
    assert "特斯拉三个字" in first_page_text
    assert "总之是，我的好奇很多" in first_page_text
    assert page_content_height(first_page) <= EFFECTIVE_TEXT_HEIGHT
    assert page_content_height(first_page) >= EFFECTIVE_TEXT_HEIGHT * 0.72


def test_paginate_keeps_orphan_lead_with_following_quote() -> None:
    article = parse_article_file(Path("content/docs/2026/06/reading-category__post-13f67e2873.md"))
    pages = paginate_blocks(article.blocks, max_chars=340)
    for page in pages:
        for index, block in enumerate(page):
            if block.text.strip() != "然后是他小时候的一次石头打鱼：":
                continue
            assert index + 1 < len(page)
            assert page[index + 1].kind == "quote"
            assert "夕阳西下" in page[index + 1].text


def test_paginate_preserves_original_paragraph_boundaries() -> None:
    article = parse_article_file(Path("content/docs/2026/06/reading-category__post-13f67e2873.md"))
    pages = paginate_blocks(article.blocks, max_chars=340)
    first_page = pages[0]
    paragraph_blocks = [block for block in first_page if block.kind == "paragraph"]
    texts = [block.text for block in paragraph_blocks]
    assert any("特斯拉汽车有关系么？" in text for text in texts)
    assert any(text.startswith("总之是，我的好奇很多") for text in texts)
    assert not any("有关系么？总之是" in text for text in texts)


def test_merge_adjacent_same_source_quotes() -> None:
    blocks = [
        ContentBlock("quote", "夕阳西下，鳟鱼十分活跃。", 11),
        ContentBlock("quote", "在这种有利条件下，随便哪个男孩都可能打中一条鱼。", 11),
        ContentBlock("paragraph", "这小时候没有经过刻意练习的石头打鱼。", 12),
    ]
    merged = _merge_adjacent_blocks(blocks)
    assert len(merged) == 2
    assert merged[0].kind == "quote"
    assert merged[0].source_id == 11
    assert "夕阳西下" in merged[0].text
    assert "在这种有利条件下" in merged[0].text


def test_paginate_keeps_full_quote_before_sparse_tail() -> None:
    article = parse_article_file(Path("content/docs/2026/06/reading-category__post-13f67e2873.md"))
    pages = paginate_blocks(article.blocks, max_chars=340)
    quote_pages = [
        index
        for index, page in enumerate(pages)
        if any(block.kind == "quote" and block.source_id == 25 for block in page)
    ]
    assert len(quote_pages) == 1
    quote_page = pages[quote_pages[0]]
    quote_blocks = [block for block in quote_page if block.kind == "quote" and block.source_id == 25]
    assert len(quote_blocks) == 1
    assert "宗教教义已经不再按其正统含义被普遍接受" in quote_blocks[0].text
    assert "超脱物质束缚的作用就行" in quote_blocks[0].text


def test_paginate_summary_mid_pages_book_fill() -> None:
    from scripts.xhs.xhs_cards.article_overflow import (
        correct_body_page_overflows,
        correct_body_page_underfills,
    )
    from scripts.xhs.xhs_cards.article_paginator import balance_body_pages

    article = parse_article_file(Path("content/docs/2026/03/summary__post-5e8573cff7.md"))
    pages = paginate_blocks(article.blocks, max_chars=340)
    pages = balance_body_pages(pages)

    header = "在我之外，还有一个安静看着我的我"
    nickname = "我要改名叫嘟嘟"

    def continues(all_pages: list, idx: int, blocks: list) -> bool:
        if idx <= 0 or not all_pages[idx - 1] or not blocks:
            return False
        previous_last = all_pages[idx - 1][-1]
        first_block = blocks[0]
        return (
            previous_last.kind == "paragraph"
            and first_block.kind == "paragraph"
            and previous_last.source_id == first_block.source_id
        )

    def render_probe(blocks: list, total: int, idx: int, all_pages: list | None = None) -> str:
        from scripts.xhs.xhs_cards.article import _render_body_page

        snapshot = all_pages if all_pages is not None else pages
        return _render_body_page(
            header,
            blocks,
            idx + 1,
            total,
            nickname,
            continues_paragraph=continues(snapshot, idx, blocks),
        )

    pages = correct_body_page_overflows(pages, render_probe)
    pages = correct_body_page_underfills(pages, render_probe)
    pages = [_merge_adjacent_blocks(page) for page in pages if page]

    for index, page in enumerate(pages[:-1]):
        ratio = page_content_height(page) / EFFECTIVE_TEXT_HEIGHT
        assert ratio >= 0.72, f"body slide {index + 1} fill {ratio:.1%}"


def test_same_paragraph_sentences_stay_together_after_job_change() -> None:
    from scripts.xhs.xhs_cards.article_overflow import (
        correct_body_page_overflows,
        correct_body_page_underfills,
    )
    from scripts.xhs.xhs_cards.article_paginator import balance_body_pages

    article = parse_article_file(Path("content/docs/2026/03/summary__post-5e8573cff7.md"))
    pages = paginate_blocks(article.blocks, max_chars=340)
    pages = balance_body_pages(pages)

    header = "在我之外，还有一个安静看着我的我"
    nickname = "我要改名叫嘟嘟"

    def continues(all_pages: list, idx: int, blocks: list) -> bool:
        if idx <= 0 or not all_pages[idx - 1] or not blocks:
            return False
        previous_last = all_pages[idx - 1][-1]
        first_block = blocks[0]
        return (
            previous_last.kind == "paragraph"
            and first_block.kind == "paragraph"
            and previous_last.source_id == first_block.source_id
        )

    def render_probe(blocks: list, total: int, idx: int, all_pages: list | None = None) -> str:
        from scripts.xhs.xhs_cards.article import _render_body_page

        snapshot = all_pages if all_pages is not None else pages
        return _render_body_page(
            header,
            blocks,
            idx + 1,
            total,
            nickname,
            continues_paragraph=continues(snapshot, idx, blocks),
        )

    pages = correct_body_page_overflows(pages, render_probe)
    pages = correct_body_page_underfills(pages, render_probe)
    pages = [_merge_adjacent_blocks(page) for page in pages if page]

    joined = "".join(block.text for page in pages for block in page)
    assert "只投一次便成功。除开这百分百命中率之外" in joined

    for page in pages:
        for block in page:
            if "只投一次便成功" in block.text:
                assert "除开这百分百命中率之外" in block.text, (
                    "sentences from the same paragraph should share one slide block"
                )
                return

    raise AssertionError("expected job-change paragraph not found in paginated output")


def test_summary_slides_06_07_fill_with_playwright() -> None:
    from scripts.xhs.xhs_cards.article_overflow import (
        _UNDERFILL_SLACK_JS,
        correct_body_page_overflows,
        correct_body_page_underfills,
    )
    from scripts.xhs.xhs_cards.article_paginator import balance_body_pages

    article = parse_article_file(Path("content/docs/2026/03/summary__post-5e8573cff7.md"))
    pages = paginate_blocks(article.blocks, max_chars=340)
    pages = balance_body_pages(pages)

    header = "在我之外，还有一个安静看着我的我"
    nickname = "我要改名叫嘟嘟"

    def continues(all_pages: list, idx: int, blocks: list) -> bool:
        if idx <= 0 or not all_pages[idx - 1] or not blocks:
            return False
        previous_last = all_pages[idx - 1][-1]
        first_block = blocks[0]
        return (
            previous_last.kind == "paragraph"
            and first_block.kind == "paragraph"
            and previous_last.source_id == first_block.source_id
        )

    def render_probe(blocks: list, total: int, idx: int, all_pages: list | None = None) -> str:
        from scripts.xhs.xhs_cards.article import _render_body_page

        snapshot = all_pages if all_pages is not None else pages
        return _render_body_page(
            header,
            blocks,
            idx + 1,
            total,
            nickname,
            continues_paragraph=continues(snapshot, idx, blocks),
        )

    pages = correct_body_page_overflows(pages, render_probe)
    pages = correct_body_page_underfills(pages, render_probe)
    pages = [_merge_adjacent_blocks(page) for page in pages if page]

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        browser_page = browser.new_page(viewport={"width": 1080, "height": 1440})
        try:
            for index in (4, 5):
                html = render_probe(pages[index], len(pages) + 2, index, pages)
                browser_page.set_content(html, wait_until="load")
                metrics = browser_page.evaluate(_UNDERFILL_SLACK_JS)
                slack = float(metrics["slack"])
                client_height = float(metrics["clientHeight"])
                ratio = slack / client_height
                assert ratio < 0.22, (
                    f"body slide {index + 1} still has {ratio:.0%} slack after underfill"
                )
        finally:
            browser.close()


def test_rendered_summary_body_slides_do_not_clip_text_area() -> None:
    from scripts.xhs.xhs_cards.article import render_article_slides
    from scripts.xhs.xhs_cards.article_browser_paginator import _BODY_FITS_JS

    manifest_path = Path(
        "scripts/xhs/output/articles/"
        "2025-nian-zhong-zong-jie-xia-ren-shi-zi-ji-hou-de-yi-ran-zuo-zi-ji/"
        "manifest.json"
    )
    slides, _ = render_article_slides(manifest_path)
    body_slides = [
        (name, html)
        for name, html in slides
        if name != "01-cover.png" and not name.endswith("-end.png")
    ]

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        browser_page = browser.new_page(viewport={"width": 1080, "height": 1440})
        try:
            overflowing: list[str] = []
            for name, html in body_slides:
                browser_page.set_content(html, wait_until="load")
                if not browser_page.evaluate(_BODY_FITS_JS):
                    overflowing.append(f"{name} overflowed")

            assert not overflowing
        finally:
            browser.close()
