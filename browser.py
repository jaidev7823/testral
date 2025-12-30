# browser.py
from playwright.sync_api import sync_playwright

def get_page(url, mobile=False):
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        viewport={"width": 375, "height": 812} if mobile else None,
        user_agent="Mozilla/5.0"
    )

    page = context.new_page()
    page.goto(url, timeout=30000)
    return p, browser, page
