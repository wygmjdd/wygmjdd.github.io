"""Parse WeChat album page to get list of article URLs. Requires Playwright."""

import re
from urllib.parse import urljoin, urlparse


def parse_album(album_url: str) -> list[str]:
    """
    Open album page with Playwright, optionally scroll to load all items,
    parse DOM for links to mp.weixin.qq.com/s, return list of article URLs.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("playwright is required: pip install playwright && playwright install chromium")

    article_urls: list[str] = []
    wechat_s_re = re.compile(r"https?://[^/]*mp\.weixin\.qq\.com/s\?[^\s\"']+", re.I)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(album_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2000)

            for _ in range(20):
                html = page.content()
                found = wechat_s_re.findall(html)
                for u in found:
                    u_clean = u.split("'")[0].split('"')[0].split(")")[0].strip()
                    if u_clean not in article_urls:
                        article_urls.append(u_clean)
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1500)
                except Exception:
                    break

            body_links = page.query_selector_all('a[href*="mp.weixin.qq.com/s"]')
            for node in body_links:
                href = node.get_attribute("href")
                if href and "mp.weixin.qq.com/s" in href:
                    full = urljoin(album_url, href)
                    parsed = urlparse(full)
                    if "mp.weixin.qq.com" in parsed.netloc and parsed.path == "/s":
                        if full not in article_urls:
                            article_urls.append(full)
        finally:
            browser.close()

    return article_urls
