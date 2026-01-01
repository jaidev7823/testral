# action.py
from shortcut import INJECT_NUMBERS, REMOVE_NUMBERS


def inject_numbers(page):
    page.evaluate(INJECT_NUMBERS)


def remove_numbers(page):
    page.evaluate(REMOVE_NUMBERS)


def click_number(page, idx: int):
    page.locator(f"[data-ai-idx='{idx}']").first.click(timeout=2000)
