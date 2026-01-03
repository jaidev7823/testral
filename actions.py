# actions.py
from shortcut import INJECT_NUMBERS, REMOVE_NUMBERS


def inject_numbers(page):
    print("[ACTION] Injecting number overlays")
    page.evaluate(INJECT_NUMBERS)


def remove_numbers(page):
    print("[ACTION] Removing number overlays")
    page.evaluate(REMOVE_NUMBERS)


def click_number(page, idx: int):
    print(f"[ACTION] Clicking data-ai-idx={idx}")

    locator = page.locator(f"[data-ai-idx='{idx}']").first

    locator.scroll_into_view_if_needed(timeout=1000)

    try:
        locator.click(timeout=2000)
    except:
        print("[ACTION] Normal click failed, forcing JS click")
        page.evaluate(
            "(el) => el.click()",
            locator
        )
