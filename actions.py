# actions.py
from shortcut import INJECT_NUMBERS, REMOVE_NUMBERS


# actions.py
def inject_numbers(page):
    # This strips non-breaking spaces and potential illegal characters
    sanitized_script = INJECT_NUMBERS.replace('\xa0', ' ')
    return page.evaluate(sanitized_script)


def remove_numbers(page):
    print("[ACTION] Removing number overlays")
    page.evaluate(REMOVE_NUMBERS)


def click_number(page, idx: int):
    print(f"[ACTION] Clicking data-ai-idx={idx}")
    page.locator(f"[data-ai-idx='{idx}']").first.click(
        timeout=2000,
        force=True
    )
