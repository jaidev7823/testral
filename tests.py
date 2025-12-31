TESTS = [
    {
        "id": "TC01",
        "name": "Search for a product",
        "run": "test_search"
    },
    {
        "id": "TC02",
        "name": "Add item to cart",
        "run": "test_add_to_cart"
    },
    {
        "id": "TC05",
        "name": "Filter products",
        "run": "test_filter"
    },
    {
        "id": "TC09",
        "name": "Mobile layout works",
        "run": "test_mobile_layout"
    },
    {
        "id": "TC10",
        "name": "Breadcrumb navigation",
        "run": "test_breadcrumb"
    }
]

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