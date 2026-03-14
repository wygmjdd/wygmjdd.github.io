"""Tests for slug_from_album."""

import pytest

from slug_from_album import slug_from_album


def test_slug_from_album_uses_pinyin_when_slug_is_none():
    assert slug_from_album("阅读书目", None) == "yuedushumu"


def test_slug_from_album_uses_provided_slug():
    assert slug_from_album("年终总结", "year-end-summary") == "year-end-summary"


def test_slug_from_album_uses_provided_slug_when_name_is_chinese():
    assert slug_from_album("三十分钟日记", "30min-diary") == "30min-diary"


def test_slug_from_album_empty_slug_falls_back_to_pinyin():
    assert slug_from_album("年终总结", "") == "nianzhongzongjie"
    assert slug_from_album("年终总结", "   ") == "nianzhongzongjie"
