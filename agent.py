# agent.py
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

from audit import run_audit, run_blocker_audit
from action import inject_numbers, remove_numbers, click_number
from shortcut import INJECT_NUMBERS, REMOVE_NUMBERS

URL = "https://bomcrewmall.com"
VIEWPORT = {"width": 1280, "height": 800}
AUDIT_FILE = "audit.md"


def run():
    Path(AUDIT_FILE).write_text(f"# Audit Log\nTarget: {URL}\n\n---\n\n")

    with sync_playwright() as p:
        page = p.chromium.launch(headless=False).new_page(viewport=VIEWPORT)
        page.goto(URL, timeout=30000)
        time.sleep(2)

        step = 0

        while True:
            step += 1

            # 1. Clean screenshot + audit
            clean_img = f"screenshots/step_{step}_clean.png"
            page.screenshot(path=clean_img, full_page=False)

            audit_text, blocked = run_audit(step, clean_img)

            # 2. If blocker suspected → ground + close
            if blocked:
                inject_numbers(page)
                time.sleep(0.3)

                num_img = f"screenshots/step_{step}_numbered.png"
                page.screenshot(path=num_img, full_page=False)

                close_idx = run_blocker_audit(step, num_img)
                if close_idx is not None:
                    click_number(page, close_idx)
                    time.sleep(1)

                remove_numbers(page)
                time.sleep(0.3)

                cleared_img = f"screenshots/step_{step}_cleared.png"
                page.screenshot(path=cleared_img, full_page=False)
                run_audit(step, cleared_img, suffix="Post Clear")

            # 3. Scroll
            prev = page.evaluate("window.scrollY")
            page.mouse.wheel(0, 600)
            time.sleep(1)

            if page.evaluate("window.scrollY") == prev:
                break

        page.close()


if __name__ == "__main__":
    run()
