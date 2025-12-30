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

def test_search(page):
    try:
        page.locator("input[type='search']").first.fill("shirt")
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        results = page.locator("a[href*='/products']").count()
        return results > 0
    except:
        return False

def test_add_to_cart(page):
    try:
        page.locator("a[href*='/products']").first.click()
        page.wait_for_timeout(1500)

        page.locator("button:has-text('Add')").first.click()
        page.wait_for_timeout(1500)

        return page.locator("[href*='cart']").count() > 0
    except:
        return False

def capture_failure(page, test_id):
    path = f"screenshots/{test_id}.png"
    page.screenshot(path=path, full_page=True)
    return path
