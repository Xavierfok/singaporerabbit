"""one-shot fb login flow.

opens chromium headed, you log in to facebook, close the browser when done.
storageState.json is saved to .auth/storageState.json for scrape.py to reuse.

run:  python3 fb_scrape/login.py
"""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
AUTH = ROOT / ".auth"
AUTH.mkdir(exist_ok=True)
STATE = AUTH / "storageState.json"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = ctx.new_page()
        page.goto("https://www.facebook.com/login")

        print("\n>>> log in to facebook in the open window.")
        print(">>> once you see your fb feed, come back here and press ENTER.")
        input(">>> ENTER to save session and close: ")

        ctx.storage_state(path=str(STATE))
        print(f"saved {STATE}")
        browser.close()


if __name__ == "__main__":
    main()
