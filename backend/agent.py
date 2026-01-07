# agent.py
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess

from audit import run_audit, run_blocker_audit
from actions import inject_numbers, remove_numbers, click_number

URL = "https://www.duroflexworld.com"
VIEWPORT = {"width": 1280, "height": 800}
AUDIT_FILE = "audit.md"


def run():
    print("[AGENT] Starting audit agent")
    Path(AUDIT_FILE).write_text(f"# Audit Log\nTarget: {URL}\n\n---\n\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport=VIEWPORT)

        print(f"[BROWSER] Navigating to {URL}")
        page.goto(URL, timeout=30000)
        time.sleep(8)

        step = 0

        while True:
            step += 1
            print(f"\n[AGENT] ===== STEP {step} =====")

            clean_img = f"screenshots/step_{step}_clean.png"
            page.screenshot(path=clean_img, full_page=False)
            print(f"[SCREENSHOT] Saved {clean_img}")

            _, blocked = run_audit(step, clean_img)

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

            # Scroll once and verify movement
            prev_scroll = page.evaluate("() => window.scrollY")

            page.evaluate("""
            () => {
                window.scrollBy(0, Math.floor(window.innerHeight * 0.85));
            }
            """)

            time.sleep(1.5)

            curr_scroll = page.evaluate("() => window.scrollY")

            if curr_scroll == prev_scroll:
                print("[AGENT] Scroll did not move — final check")

                _, blocked = run_audit(step, clean_img, suffix="Final Check")

                if blocked:
                    print("[AGENT] Blocker present at final state (logged only)")
                else:
                    print("[AGENT] No blocker at final state")

                print("[AGENT] True page end confirmed. Stopping audit.")
                break

        browser.close()
        print("[AGENT] Audit complete")

    print("[POST] Running post_process.py")
    subprocess.run(["python", "post_process.py"], check=True)


if __name__ == "__main__":
    run()
