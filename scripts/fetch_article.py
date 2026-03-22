"""Fetch a single WeChat article URL and return title, date, body_md, source_url."""

from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import html2text
import requests
from bs4 import BeautifulSoup, Tag

_REPO_ROOT = Path(__file__).resolve().parent.parent
_STATIC_IMAGES_WECHAT = _REPO_ROOT / "static" / "images" / "wechat"
_MIN_IMAGE_BYTES = 256
_REFERER_WECHAT = "https://mp.weixin.qq.com/"
_CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _fetch_html_playwright(url: str, timeout_ms: int = 30000) -> str:
    """Load URL in headless browser and return full HTML. Used when requests returns empty body."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_selector("#js_content", timeout=timeout_ms)
            page.wait_for_timeout(1500)
            return page.content()
        finally:
            browser.close()


def fetch_article(url: str, download_images: bool = True) -> dict:
    """Fetch article page, extract title, publish date, and body; convert body to Markdown."""
    html_text = _get_html(url)
    return _parse_article_html(html_text, url, download_images=download_images)


def _get_html(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    html_text = resp.text
    soup = BeautifulSoup(html_text, "html.parser")
    if _extract_body(soup) or _extract_title(soup):
        return html_text
    print(
        "    [fetch_article] HTML from requests has no #js_content/title — "
        "launching Playwright (Chromium) for this article…",
        flush=True,
    )
    try:
        return _fetch_html_playwright(url)
    except Exception as e:
        raise RuntimeError(
            f"WeChat page needs JavaScript to render content. Request with browser failed: {e}. "
            "Install Playwright browsers: pip install playwright && playwright install"
        ) from e


def _canonical_article_url(url: str) -> str:
    return html.unescape(url.strip()).split("#")[0]


def _img_real_url(img: Tag, page_url: str) -> str | None:
    for attr in ("data-src", "data-original", "src"):
        raw = img.get(attr)
        if not raw or not isinstance(raw, str):
            continue
        v = raw.strip()
        if not v or v.lower().startswith("data:"):
            continue
        if v.startswith("//"):
            v = "https:" + v
        elif not v.startswith("http://") and not v.startswith("https://"):
            v = urljoin(page_url, v)
        if not (v.startswith("http://") or v.startswith("https://")):
            continue
        return v
    return None


def _sniff_image_extension(data: bytes, fallback_url: str) -> str:
    if len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if len(data) >= 2 and data[:2] == b"\xff\xd8":
        return ".jpg"
    if len(data) >= 6 and data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    path = urlparse(fallback_url).path.lower()
    for ext in (".png", ".webp", ".gif", ".jpeg", ".jpg"):
        if path.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def _ext_from_content_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    ct = content_type.lower()
    if "png" in ct:
        return ".png"
    if "webp" in ct:
        return ".webp"
    if "gif" in ct:
        return ".gif"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"
    return None


def _try_requests_image(url: str, referer: str) -> tuple[bytes, str | None] | None:
    headers = {
        "User-Agent": _CHROME_UA,
        "Referer": referer,
    }
    try:
        r = requests.get(url, headers=headers, timeout=45)
        r.raise_for_status()
        data = r.content
        if len(data) < _MIN_IMAGE_BYTES:
            return None
        ct = r.headers.get("Content-Type")
        return data, ct
    except Exception:
        return None


def _playwright_download_images(urls: list[str]) -> dict[str, bytes]:
    """Fetch bytes for URLs that hotlink-block requests; one short browser session."""
    result: dict[str, bytes] = {}
    if not urls:
        return result
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return result
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(_REFERER_WECHAT, wait_until="domcontentloaded", timeout=25000)
            for u in urls:
                try:
                    resp = context.request.get(u, timeout=60000)
                    if resp.status != 200:
                        continue
                    data = resp.body()
                    if len(data) >= _MIN_IMAGE_BYTES:
                        result[u] = data
                except Exception:
                    continue
        finally:
            browser.close()
    return result


def _localize_wechat_images(content: Tag, source_url: str) -> None:
    canonical = _canonical_article_url(source_url)
    article_key = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
    out_dir = _STATIC_IMAGES_WECHAT / article_key
    out_dir.mkdir(parents=True, exist_ok=True)

    pairs: list[tuple[Tag, str]] = []
    for img in content.find_all("img"):
        raw = _img_real_url(img, canonical)
        if raw:
            pairs.append((img, raw))
    if not pairs:
        return

    unique_urls = list(dict.fromkeys(u for _, u in pairs))
    print(
        f"    [fetch_article] images: {len(pairs)} <img> tag(s), {len(unique_urls)} unique URL(s) "
        f"→ static/images/wechat/{article_key}/",
        flush=True,
    )
    url_bytes: dict[str, bytes] = {}
    url_ct: dict[str, str | None] = {}

    failed: list[str] = []
    for u in unique_urls:
        got = _try_requests_image(u, _REFERER_WECHAT)
        if got is None:
            failed.append(u)
            continue
        data, ct = got
        url_bytes[u] = data
        url_ct[u] = ct

    if failed:
        print(
            f"    [fetch_article] requests failed for {len(failed)}/{len(unique_urls)} image(s); "
            "retrying via Playwright…",
            flush=True,
        )
        pw = _playwright_download_images(failed)
        for u in failed:
            if u in pw:
                url_bytes[u] = pw[u]
                url_ct[u] = None

    written_rel: dict[str, str] = {}
    seq = 0
    for img, u in pairs:
        data = url_bytes.get(u)
        if not data:
            continue
        if u not in written_rel:
            seq += 1
            ext = _ext_from_content_type(url_ct.get(u)) or _sniff_image_extension(data, u)
            filename = f"{seq:03d}{ext}"
            abs_path = out_dir / filename
            abs_path.write_bytes(data)
            written_rel[u] = f"/images/wechat/{article_key}/{filename}"
        img["src"] = written_rel[u]
        for attr in list(img.attrs):
            if attr != "src" and (attr.startswith("data-") or attr in ("crossorigin",)):
                del img[attr]

    if seq > 0:
        print(f"    [fetch_article] wrote {seq} image file(s) under /images/wechat/{article_key}/", flush=True)
    elif pairs:
        print(
            "    [fetch_article] warning: no image bytes saved (hotlink or network); "
            "markdown may still show broken/remote images",
            flush=True,
        )


def _parse_article_html(html: str, source_url: str, download_images: bool = True) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = _extract_title(soup)
    date = _extract_date(soup)
    content = soup.find(id="js_content")
    if content is not None and download_images:
        _localize_wechat_images(content, source_url)
    body_html = str(content) if content else ""
    body_md = _html_to_markdown(body_html)
    return {
        "title": title,
        "date": date,
        "body_md": body_md,
        "source_url": source_url,
    }


def _extract_title(soup: BeautifulSoup) -> str:
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()
    title_tag = soup.find("title")
    return title_tag.get_text().strip() if title_tag else ""


def _parse_chinese_date(text: str) -> str | None:
    """Parse 'YYYY年M月D日' or 'YYYY年M月D日 HH:MM' from page text. Returns YYYY-MM-DD or None."""
    match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if not match:
        return None
    y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if 1 <= m <= 12 and 1 <= d <= 31:
        try:
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def _extract_date(soup: BeautifulSoup):
    meta = soup.find("meta", attrs={"name": "publish_time"})
    if meta and meta.get("content"):
        raw = meta["content"].strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(raw[:19], fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    visible = soup.get_text(separator=" ", strip=False)
    head_and_meta = visible[:3000]
    chinese_date = _parse_chinese_date(head_and_meta)
    if chinese_date:
        return chinese_date
    script_text = " ".join(s.get_text() for s in soup.find_all("script") if s.get_text())
    match = re.search(r'"(\d{10})"', script_text)
    if match:
        try:
            ts = int(match.group(1))
            return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        except (ValueError, OSError):
            pass
    return datetime.utcnow().strftime("%Y-%m-%d")


def _extract_body(soup: BeautifulSoup) -> str:
    content = soup.find(id="js_content")
    if content:
        return str(content)
    return ""


def _html_to_markdown(html_fragment: str) -> str:
    if not html_fragment:
        return ""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0
    return h.handle(html_fragment).strip()
