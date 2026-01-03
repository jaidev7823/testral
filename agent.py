# agent.py
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

from audit import run_audit, run_blocker_audit
from actions import inject_numbers, remove_numbers, click_number

URL = "https://google.com"
VIEWPORT = {"width": 1280, "height": 800}
AUDIT_FILE = "audit.md"


def run():
    print("[AGENT] Starting audit agent")
    Path(AUDIT_FILE).write_text(f"# Audit Log\nTarget: {URL}\n\n---\n\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport=VIEWPORT)

        page.goto(URL, timeout=30000)
        time.sleep(7)

        step = 0

        while True:
            step += 1
            print(f"\n[AGENT] ===== STEP {step} =====")

            clean_img = f"screenshots/step_{step}_clean.png"
            page.screenshot(path=clean_img, full_page=False)

            _, blocked = run_audit(step, clean_img)

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

                cleared_img = f"screenshots/step_{step}_cleared.png"
                page.screenshot(path=cleared_img, full_page=False)

                run_audit(step, cleared_img, suffix="Post Clear")

            page.evaluate("""
                () => window.scrollBy(0, Math.floor(window.innerHeight * 0.85))
            """)
            time.sleep(1.5)

            is_end = page.evaluate("""
                () => {
                    const scrollBottom = window.scrollY + window.innerHeight;
                    const pageHeight = document.documentElement.scrollHeight;
                    return (pageHeight - scrollBottom) < 50;
                }
            """)

            if is_end:
                verify_img = f"screenshots/step_{step}_verify_end.png"
                page.screenshot(path=verify_img, full_page=False)

                _, blocked = run_audit(step, verify_img, suffix="End Check")

                if not blocked:
                    break

        browser.close()
        print("[AGENT] Audit complete")


if __name__ == "__main__":
    run()

    import subprocess
    subprocess.run(["python", "post_process.py"], check=True)
