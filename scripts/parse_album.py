"""Parse WeChat album page to get list of article URLs. Requires Playwright."""

import re
from urllib.parse import urljoin, urlparse


def parse_album(album_url: str, verbose: bool = True) -> list[str]:
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

    def _v(msg: str) -> None:
        if verbose:
            print(msg, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            _v("      → Playwright: loading album page (networkidle, up to 60s)…")
            page.goto(album_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2000)

            for pass_i in range(1, 21):
                html = page.content()
                found = wechat_s_re.findall(html)
                for u in found:
                    u_clean = u.split("'")[0].split('"')[0].split(")")[0].strip()
                    if u_clean not in article_urls:
                        article_urls.append(u_clean)
                if pass_i == 1 or pass_i % 5 == 0 or pass_i == 20:
                    _v(f"      → scroll pass {pass_i}/20 · {len(article_urls)} article links seen")
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1500)
                except Exception:
                    break

            _v("      → scanning <a> elements for /s links…")
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

    _v(f"      → album parse finished · {len(article_urls)} unique article URLs")
    return article_urls
