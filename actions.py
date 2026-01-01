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
    page.locator(f"[data-ai-idx='{idx}']").first.click(timeout=2000)
