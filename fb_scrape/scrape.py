"""scrape facebook pages + groups using a saved login session.

reads urls.txt (type,url,slug), loads storageState from .auth/, and for each
source extracts the latest N posts: text, date, author, image refs, comments.
images are downloaded into <slug>/images/. metadata is one json per source.

run:  python3 fb_scrape/scrape.py [--max-posts 20] [--only slug1,slug2]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from playwright.sync_api import Browser, BrowserContext, Page, TimeoutError as PWTimeout, sync_playwright

ROOT = Path(__file__).parent
AUTH = ROOT / ".auth" / "storageState.json"
URLS = ROOT / "urls.txt"
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def log(msg: str, *, slug: str = "scrape") -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with (LOGS / f"{slug}.log").open("a") as f:
        f.write(line + "\n")


def load_urls() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in URLS.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            log(f"skipping malformed line: {line!r}")
            continue
        kind, url, slug = parts
        if slug in seen:
            log(f"skipping duplicate slug: {slug}")
            continue
        seen.add(slug)
        rows.append({"type": kind, "url": url, "slug": slug})
    return rows


def out_dir(row: dict[str, str]) -> Path:
    bucket = "pages" if row["type"] == "page" else "groups"
    d = ROOT / bucket / row["slug"]
    (d / "images").mkdir(parents=True, exist_ok=True)
    return d


def dismiss_dialogs(page: Page) -> None:
    """close cookie banners, login walls, notification prompts."""
    for sel in [
        '[aria-label="Decline optional cookies"]',
        '[aria-label="Allow all cookies"]',
        '[aria-label="Close"]',
        'div[role="dialog"] [aria-label="Close"]',
    ]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=500):
                el.click(timeout=1500)
                page.wait_for_timeout(400)
        except Exception:
            pass


def scroll_for_posts(page: Page, max_posts: int, max_scrolls: int = 40) -> None:
    """scroll until N feed articles are present or we hit cap."""
    last_h = 0
    stale = 0
    for _ in range(max_scrolls):
        count = page.locator('div[role="article"]').count()
        if count >= max_posts:
            return
        page.mouse.wheel(0, 4000)
        page.wait_for_timeout(1500)
        h = page.evaluate("document.body.scrollHeight")
        if h == last_h:
            stale += 1
            if stale >= 3:
                return
        else:
            stale = 0
        last_h = h


def extract_metadata(page: Page, row: dict[str, str]) -> dict[str, Any]:
    md: dict[str, Any] = {
        "type": row["type"],
        "url": row["url"],
        "slug": row["slug"],
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "title": None,
        "about": None,
    }
    try:
        md["title"] = page.title()
    except Exception:
        pass
    # try common about hooks
    for sel in ['div[data-pagelet="ProfileTilesFeed"]', 'div[role="main"] h1']:
        try:
            t = page.locator(sel).first.inner_text(timeout=1500)
            if t:
                md.setdefault("snippets", []).append(t.strip()[:500])
        except Exception:
            continue
    return md


def parse_post(article) -> dict[str, Any]:
    post: dict[str, Any] = {"text": "", "author": None, "permalink": None, "timestamp_label": None, "images": [], "comment_excerpt": []}
    try:
        post["text"] = article.inner_text(timeout=2000).strip()
    except Exception:
        pass
    try:
        author_el = article.locator('h3 a, h2 a, strong a').first
        post["author"] = author_el.inner_text(timeout=1000).strip()
    except Exception:
        pass
    try:
        link_el = article.locator('a[href*="/posts/"], a[href*="/permalink/"], a[href*="story_fbid"]').first
        href = link_el.get_attribute("href", timeout=1000)
        if href:
            post["permalink"] = href.split("?")[0] if href.startswith("http") else f"https://www.facebook.com{href.split('?')[0]}"
    except Exception:
        pass
    try:
        ts_el = article.locator('a[role="link"] span:has-text("·"), abbr, a[aria-label*="20"]').first
        post["timestamp_label"] = ts_el.inner_text(timeout=800).strip()
    except Exception:
        pass
    try:
        imgs = article.locator('img[src*="scontent"]').all()
        for img in imgs[:6]:
            src = img.get_attribute("src")
            alt = img.get_attribute("alt") or ""
            if src:
                post["images"].append({"url": src, "alt": alt.strip()})
    except Exception:
        pass
    return post


def download_images(client: httpx.Client, post: dict[str, Any], img_dir: Path, post_idx: int) -> None:
    for n, img in enumerate(post["images"]):
        url = img["url"]
        ext = ".jpg"
        m = re.search(r"\.(jpg|jpeg|png|webp)", urlparse(url).path)
        if m:
            ext = "." + m.group(1).lower().replace("jpeg", "jpg")
        fname = f"post{post_idx:03d}_{n:02d}{ext}"
        try:
            r = client.get(url, timeout=20)
            if r.status_code == 200 and r.content:
                (img_dir / fname).write_bytes(r.content)
                img["local"] = f"images/{fname}"
        except Exception as e:
            log(f"img dl failed: {e}")


def expand_top_comments(article, take: int = 3) -> list[str]:
    """try to surface a few top-level comments (best-effort, skipped if walled)."""
    out: list[str] = []
    try:
        for span in article.locator('div[aria-label="Comment"] [dir="auto"]').all()[:take]:
            t = span.inner_text(timeout=500).strip()
            if t:
                out.append(t[:500])
    except Exception:
        pass
    return out


def scrape_one(ctx: BrowserContext, row: dict[str, str], max_posts: int) -> None:
    slug = row["slug"]
    log(f"open {row['url']}", slug=slug)
    page = ctx.new_page()
    page.set_default_timeout(15000)
    try:
        page.goto(row["url"], wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        dismiss_dialogs(page)
        page.wait_for_timeout(1500)

        if "login" in page.url or page.locator('input[name="email"]').is_visible(timeout=1000):
            log("WARNING: appears to be logged out — skipping", slug=slug)
            return

        scroll_for_posts(page, max_posts)
        articles = page.locator('div[role="article"]').all()[:max_posts]
        log(f"found {len(articles)} articles", slug=slug)

        odir = out_dir(row)
        img_dir = odir / "images"
        metadata = extract_metadata(page, row)

        posts: list[dict[str, Any]] = []
        with httpx.Client(headers={"User-Agent": UA, "Referer": "https://www.facebook.com/"}) as client:
            for idx, art in enumerate(articles):
                try:
                    post = parse_post(art)
                    post["comment_excerpt"] = expand_top_comments(art)
                    download_images(client, post, img_dir, idx)
                    posts.append(post)
                except Exception as e:
                    log(f"post {idx} parse failed: {e}", slug=slug)

        (odir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
        (odir / "posts.json").write_text(json.dumps(posts, indent=2, ensure_ascii=False))
        log(f"wrote {len(posts)} posts -> {odir}", slug=slug)
    except PWTimeout as e:
        log(f"timeout: {e}", slug=slug)
    finally:
        page.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-posts", type=int, default=20)
    ap.add_argument("--only", default="", help="comma-sep slugs to scrape (default: all)")
    args = ap.parse_args()

    if not AUTH.exists():
        print(f"missing {AUTH}. run python3 fb_scrape/login.py first.", file=sys.stderr)
        sys.exit(1)

    rows = load_urls()
    if args.only:
        wanted = {s.strip() for s in args.only.split(",") if s.strip()}
        rows = [r for r in rows if r["slug"] in wanted]
    log(f"scraping {len(rows)} sources, max_posts={args.max_posts}")

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(
            storage_state=str(AUTH),
            user_agent=UA,
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        try:
            for row in rows:
                scrape_one(ctx, row, args.max_posts)
                time.sleep(4)  # polite gap between sources
        finally:
            ctx.close()
            browser.close()


if __name__ == "__main__":
    main()
