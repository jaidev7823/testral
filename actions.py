from playwright.sync_api import sync_playwright, TimeoutError, Error
import re
import time

TARGET_TEXT = re.compile(r"womens\s*pilot\s*shirt", re.I)

def collect_candidates(page):
    candidates = []
    elements = page.locator("a, button, input[type=submit], [role=button]")
    count = elements.count()
    for i in range(count):
        el = elements.nth(i)
        try:
            if not el.is_visible():
                continue
            box = el.bounding_box()
            if not box or box["width"] == 0 or box["height"] == 0:
                continue
            text = (el.inner_text() or "").strip()
            aria = el.get_attribute("aria-label")
            if TARGET_TEXT.search(text) or TARGET_TEXT.search(aria or ""):
                candidates.append({
                    "id": f"el_{len(candidates)}",
                    "element": el,
                    "text": text,
                    "box": box,
                    "tag": el.evaluate("e => e.tagName.toLowerCase()"),
                })
        except Exception:
            continue
    # Sort by vertical position (y) — more likely to be in main content
    candidates.sort(key=lambda c: c["box"]["y"])
    return candidates


def main(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        print(f"\nOpening: {url}")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        print("\nCollecting 'Shop Now' candidates...")
        candidates = collect_candidates(page)

        if not candidates:
            print("❌ No 'Shop Now' buttons found at all.")
            browser.close()
            return

        print(f"Found {len(candidates)} 'Shop Now' candidates (sorted by position):")
        for i, c in enumerate(candidates):
            y = c["box"]["y"]
            print(f"  {c['id']} | y={int(y)} | {c['text'][:40]}")

        success = False
        for i, c in enumerate(candidates):
            print(f"\n➡️ Trying candidate {i+1}/{len(candidates)}: '{c['text']}' (y={int(c['box']['y'])})")
            try:
                # Scroll it into view
                c["element"].scroll_into_view_if_needed()
                page.wait_for_timeout(300)

                # Attempt click (without force first, then with force if needed)
                try:
                    c["element"].click(timeout=5000)
                except (TimeoutError, Error):
                    print("  ⚠️ Regular click failed. Trying with force=True...")
                    c["element"].click(force=True, timeout=5000)

                print(f"✅ SUCCESS! Clicked '{c['text']}'")
                success = True
                break

            except Exception as e:
                print(f"  ❌ Failed: {str(e)[:100]}")
                continue

        if not success:
            print("\n🛑 All 'Shop Now' buttons failed to click.")
        else:
            print("\n⏸️ Click succeeded. Waiting... (Press CTRL+C to exit)")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nAborted by user.")

        browser.close()


if __name__ == "__main__":
    main("https://bomcrewmall.com")