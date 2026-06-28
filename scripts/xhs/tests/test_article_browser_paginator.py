from __future__ import annotations

from pathlib import Path

from scripts.xhs.xhs_cards.article import _render_body_page
from scripts.xhs.xhs_cards.article_parser import ContentBlock, parse_article_file
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


def test_browser_paginator_backfills_renderable_prefix_on_underfilled_page() -> None:
    article = parse_article_file(Path("content/docs/2026/03/summary__post-5e8573cff7.md"))

    pages = paginate_blocks_with_browser(article.blocks, _render_probe, max_chars=340)

    page_texts = ["".join(block.text for block in page) for page in pages]
    assert not any(text.startswith("（关于游戏充钱") for text in page_texts[1:])
    assert any(
        "（关于游戏充钱甚至为——不只是我——沉迷花钱这件事" in text
        for text in page_texts[:-1]
    )


def test_browser_paginator_backfills_one_line_prefix_at_near_pixel_boundary() -> None:
    article = parse_article_file(Path("content/docs/2026/03/summary__post-5e8573cff7.md"))

    pages = paginate_blocks_with_browser(article.blocks, _render_probe, max_chars=340)

    assert len(pages) >= 3
    assert pages[1][-1].source_id == 10
    assert pages[1][-1].text.startswith("我想依然是")


def test_browser_paginator_does_not_leave_punctuation_at_page_start_after_backfill() -> None:
    article = parse_article_file(Path("content/docs/2026/03/summary__post-5e8573cff7.md"))

    pages = paginate_blocks_with_browser(article.blocks, _render_probe, max_chars=340)

    page_texts = ["".join(block.text for block in page) for page in pages]
    assert not any(text.startswith("。") for text in page_texts[1:])
