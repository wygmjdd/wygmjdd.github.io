"""Fetch a single WeChat article URL and return title, date, body_md, source_url."""

import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import html2text


def fetch_article(url: str) -> dict:
    """Fetch article page, extract title, publish date, and body; convert body to Markdown."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = _extract_title(soup)
    date = _extract_date(soup)
    body_html = _extract_body(soup)
    body_md = _html_to_markdown(body_html)

    return {
        "title": title,
        "date": date,
        "body_md": body_md,
        "source_url": url,
    }


def _extract_title(soup: BeautifulSoup) -> str:
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()
    title_tag = soup.find("title")
    return title_tag.get_text().strip() if title_tag else ""


def _extract_date(soup: BeautifulSoup):
    meta = soup.find("meta", attrs={"name": "publish_time"})
    if meta and meta.get("content"):
        raw = meta["content"].strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(raw[:19], fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
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
