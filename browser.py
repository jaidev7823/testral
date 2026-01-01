import os
from playwright.sync_api import sync_playwright

# Global Playwright context (v0 simple)
_playwright = None
_browser = None


def open_page(url: str):
    global _playwright, _browser

    if _playwright is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=False)

    page = _browser.new_page(
        viewport={"width": 1280, "height": 800}
    )

    page.goto(url, timeout=60000)
    page.wait_for_load_state("networkidle")

    return page


def take_screenshot(page, step: int):
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/step_{step}.png"

    page.screenshot(path=path, full_page=False)
    return path


def scroll_page(page, pixels: int = 600):
    """
    Scrolls the page.
    Returns False if cannot scroll further.
    """

    prev_y = page.evaluate("window.scrollY")
    page.mouse.wheel(0, pixels)
    page.wait_for_timeout(1000)
    new_y = page.evaluate("window.scrollY")

    return new_y > prev_y
