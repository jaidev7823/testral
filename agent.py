# agent.py
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

from audit import run_audit, run_blocker_audit
from actions import inject_numbers, remove_numbers, click_number

URL = "https://bomcrewmall.com"
VIEWPORT = {"width": 1280, "height": 800}
AUDIT_FILE = "audit.md"


def run():
    print("[AGENT] Starting audit agent")
    Path(AUDIT_FILE).write_text(f"# Audit Log\nTarget: {URL}\n\n---\n\n")

    with sync_playwright() as p:
        print("[BROWSER] Launching Chromium (headless)")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT)

        print(f"[BROWSER] Navigating to {URL}")
        page.goto(URL, timeout=30000)
        time.sleep(2)

        step = 0

        while True:
            step += 1
            print(f"\n[AGENT] ===== STEP {step} =====")

            # 1. Clean screenshot + audit
            clean_img = f"screenshots/step_{step}_clean.png"
            page.screenshot(path=clean_img, full_page=False)
            print(f"[SCREENSHOT] Saved {clean_img}")

            _, blocked = run_audit(step, clean_img)

            # 2. Handle blocker
            if blocked:
                print("[AGENT] Blocker detected, attempting removal")
                inject_numbers(page)
                time.sleep(0.3)

                num_img = f"screenshots/step_{step}_numbered.png"
                page.screenshot(path=num_img, full_page=False)
                print(f"[SCREENSHOT] Saved {num_img}")

                close_idx = run_blocker_audit(step, num_img)
                if close_idx is not None:
                    print(f"[ACTION] Clicking element {close_idx}")
                    click_number(page, close_idx)
                    time.sleep(1)
                else:
                    print("[ACTION] No close button identified")

                remove_numbers(page)

                cleared_img = f"screenshots/step_{step}_cleared.png"
                page.screenshot(path=cleared_img, full_page=False)
                print(f"[SCREENSHOT] Saved {cleared_img}")

                run_audit(step, cleared_img, suffix="Post Clear")

            # 3. Scroll
            prev = page.evaluate("window.scrollY")
            page.mouse.wheel(0, 600)
            time.sleep(1)

            if page.evaluate("window.scrollY") == prev:
                print("[AGENT] Reached bottom of page")
                break

        browser.close()
        print("[AGENT] Audit complete")


if __name__ == "__main__":
    run()
