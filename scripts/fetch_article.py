"""Fetch a single WeChat article URL and return title, date, body_md, source_url."""

import re
from datetime import datetime

import html2text
import requests
from bs4 import BeautifulSoup


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


def fetch_article(url: str) -> dict:
    """Fetch article page, extract title, publish date, and body; convert body to Markdown."""
    html = _get_html(url)
    return _parse_article_html(html, url)


def _get_html(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    if _extract_body(soup) or _extract_title(soup):
        return html
    try:
        return _fetch_html_playwright(url)
    except Exception as e:
        raise RuntimeError(
            f"WeChat page needs JavaScript to render content. Request with browser failed: {e}. "
            "Install Playwright browsers: pip install playwright && playwright install"
        ) from e


def _parse_article_html(html: str, source_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = _extract_title(soup)
    date = _extract_date(soup)
    body_html = _extract_body(soup)
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


def _html_to_markdown(html: str) -> str:
    if not html:
        return ""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0
    return h.handle(html).strip()
