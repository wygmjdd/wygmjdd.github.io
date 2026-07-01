"""Tests for slug_from_album."""

import pytest

from scripts.wechat.slug_from_album import slug_from_album


def test_slug_from_album_uses_pinyin_when_slug_is_none():
    assert slug_from_album("阅读书目", None) == "yue-du-shu-mu"


def test_slug_from_album_uses_album_name_over_legacy_slug():
    assert slug_from_album("总结", "summary") == "zong-jie"


def test_slug_from_album_handles_digits_and_chinese():
    assert slug_from_album("30分钟日记", "30min-diary") == "30-fen-zhong-ri-ji"


def test_slug_from_album_empty_slug_falls_back_to_pinyin():
    assert slug_from_album("年终总结", "") == "nian-zhong-zong-jie"
    assert slug_from_album("年终总结", "   ") == "nian-zhong-zong-jie"
