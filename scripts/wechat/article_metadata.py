"""Read lightweight metadata from a WeChat article using only the standard library."""

from __future__ import annotations

import ast
import html
import re
import time
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

REFERER_WECHAT = "https://mp.weixin.qq.com/"
CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class ArticlePageMetadata:
    album_title: str | None = None
    article_key: str | None = None


def _extract_js_string_field(text: str, field: str) -> str | None:
    match = re.search(
        rf"(?:[\"']?{re.escape(field)}[\"']?)\s*:\s*([\"'])((?:\\.|(?!\1).)*)\1",
        text,
        re.DOTALL,
    )
    if not match:
        return None
    quote = match.group(1)
    value = match.group(2).replace(r"\/", "/")
    try:
        decoded = ast.literal_eval(f"{quote}{value}{quote}")
        if isinstance(decoded, str):
            value = decoded
    except (SyntaxError, ValueError):
        value = value.replace(r"\'", "'").replace(r'\"', '"')
    return html.unescape(value).strip() or None


def extract_album_title(html_text: str) -> str | None:
    album = re.search(r"""["']?appmsgalbuminfo["']?\s*:\s*\{""", html_text)
    if album:
        album_fields = html_text[album.end() : album.end() + 2000]
        title = _extract_js_string_field(album_fields, "title")
        if title:
            return title

    return _extract_js_string_field(html_text, "tag_name")


def _build_article_key(biz: str | None, mid: str | None, idx: str | None, sn: str | None) -> str | None:
    values = [html.unescape(str(value or "")).strip() for value in (biz, mid, idx, sn)]
    if not all(values):
        return None
    return "|".join(values)


def extract_article_key_from_url(url: str) -> str | None:
    query = parse_qs(urlsplit(html.unescape(url.strip())).query)

    def first(name: str) -> str | None:
        values = query.get(name)
        return values[0] if values else None

    return _build_article_key(first("__biz"), first("mid"), first("idx"), first("sn"))


def extract_article_key(html_text: str) -> str | None:
    report = re.search(r"""["']?reportOpt["']?\s*:\s*\{""", html_text)
    if report:
        fields = html_text[report.end() : report.end() + 2000]
        key = _build_article_key(
            _extract_js_string_field(fields, "biz"),
            _extract_js_string_field(fields, "mid"),
            _extract_js_string_field(fields, "idx"),
            _extract_js_string_field(fields, "sn"),
        )
        if key:
            return key

    og_url = re.search(
        r"""<meta\s+[^>]*property=["']og:url["'][^>]*content=["'](.*?)["']""",
        html_text,
        re.IGNORECASE | re.DOTALL,
    )
    if og_url:
        return extract_article_key_from_url(og_url.group(1))
    return None


def extract_article_metadata(html_text: str) -> ArticlePageMetadata:
    return ArticlePageMetadata(
        album_title=extract_album_title(html_text),
        article_key=extract_article_key(html_text),
    )


def fetch_article_metadata(
    url: str,
    *,
    timeout: float = 30,
    attempts: int = 2,
) -> ArticlePageMetadata:
    attempts = max(1, attempts)
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": CHROME_UA,
                    "Referer": REFERER_WECHAT,
                },
            )
            with urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                html_text = response.read().decode(charset, errors="replace")
            metadata = extract_article_metadata(html_text)
            if metadata.article_key:
                return metadata
            last_error = ValueError("WeChat response did not contain a stable article identity")
        except Exception as exc:
            last_error = exc

        if attempt + 1 < attempts:
            time.sleep(0.5)

    assert last_error is not None
    raise last_error


def fetch_article_album_title(url: str, *, timeout: float = 30) -> str | None:
    return fetch_article_metadata(url, timeout=timeout).album_title
