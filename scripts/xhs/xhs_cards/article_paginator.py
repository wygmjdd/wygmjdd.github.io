"""Paginate article content blocks into Xiaohongshu slide pages."""

from __future__ import annotations

import re

from scripts.xhs.xhs_cards.article_parser import ContentBlock

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？；])")


def char_count(text: str) -> int:
    return len(text.strip())


def split_sentences(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    parts = _SENTENCE_SPLIT_RE.split(stripped)
    sentences: list[str] = []
    buffer = ""
    for part in parts:
        buffer += part
        if part and part[-1] in "。！？；" and buffer.strip():
            sentences.append(buffer.strip())
            buffer = ""
    if buffer.strip():
        sentences.append(buffer.strip())
    return sentences


def split_block_to_chunks(block: ContentBlock, max_chars: int) -> list[ContentBlock]:
    if char_count(block.text) <= max_chars:
        return [block]

    sentences = split_sentences(block.text)
    if len(sentences) <= 1:
        mid = max(1, len(block.text) // 2)
        return [
            ContentBlock(block.kind, block.text[:mid].strip()),
            ContentBlock(block.kind, block.text[mid:].strip()),
        ]

    chunks: list[ContentBlock] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current}{sentence}" if current else sentence
        if char_count(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(ContentBlock(block.kind, current))
        current = sentence
    if current.strip():
        chunks.append(ContentBlock(block.kind, current.strip()))
    return chunks


def paginate_blocks(blocks: list[ContentBlock], max_chars: int) -> list[list[ContentBlock]]:
    pages: list[list[ContentBlock]] = []
    current_page: list[ContentBlock] = []
    current_chars = 0

    def flush() -> None:
        nonlocal current_page, current_chars
        if current_page:
            pages.append(current_page)
            current_page = []
            current_chars = 0

    for block in blocks:
        for chunk in split_block_to_chunks(block, max_chars):
            chunk_len = char_count(chunk.text)
            if current_page and current_chars + chunk_len > max_chars:
                flush()
            current_page.append(chunk)
            current_chars += chunk_len

    flush()
    return pages
