from __future__ import annotations

from scripts.xhs.xhs_cards.article_parser import ContentBlock
from scripts.xhs.xhs_cards.article_paginator import paginate_blocks, split_sentences


def test_split_sentences() -> None:
    text = "第一句。第二句！第三句？"
    assert split_sentences(text) == ["第一句。", "第二句！", "第三句？"]


def test_paginate_keeps_short_blocks_together() -> None:
    blocks = [
        ContentBlock("paragraph", "短段一。"),
        ContentBlock("quote", "引用块。"),
        ContentBlock("paragraph", "短段二。"),
    ]
    pages = paginate_blocks(blocks, max_chars=200)
    assert len(pages) == 1
    assert len(pages[0]) == 3


def test_paginate_splits_long_paragraph_by_sentence() -> None:
    long_text = "。".join([f"第{i}句" for i in range(1, 12)]) + "。"
    blocks = [ContentBlock("paragraph", long_text)]
    pages = paginate_blocks(blocks, max_chars=30)
    assert len(pages) >= 2
    joined = "".join(block.text for page in pages for block in page)
    assert "第1句" in joined
    assert "第11句" in joined
