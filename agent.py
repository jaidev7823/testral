from browser import open_page, take_screenshot, scroll_page
from audit import run_audit
from actions import close_blocker, click_by_text
import time

def run(url):
    print(f"[AGENT] Starting audit for: {url}")

    page = open_page(url)

    step = 0
    while True:
        time.sleep(5)  # wait 5 seconds before taking any step

        step += 1
        print(f"[AGENT] Step {step}")

        screenshot = take_screenshot(page, step)
        print(f"[AGENT] Screenshot saved: {screenshot}")

        audit = run_audit(screenshot)

        # Persist audit result to audit.md (append)
        try:
            with open("audit.md", "a", encoding="utf-8") as f:
                f.write(f"## Step {step}\n")
                f.write(f"- Screenshot: {screenshot}\n")
                f.write("- QC Report:\n\n")
                f.write("```")
                f.write((audit.get("qc_report") or "") + "\n")
                f.write("```\n")
                suspected = audit.get("blocker_hint", {}).get("suspected")
                f.write(f"- Blocker suspected: {'Yes' if suspected else 'No'}\n")
                hint_text = audit.get("blocker_hint", {}).get("hint_text")
                if hint_text:
                    f.write(f"- Blocker hint: {hint_text}\n")
                f.write("\n")
        except Exception:
            pass

        # --- Handle possible blocker ---
        if audit["blocker_hint"]["suspected"]:
            print("[AGENT] Possible blocker detected")
            closed = close_blocker(page, audit["blocker_hint"])
            if closed:
                print("[AGENT] Blocker closed, retrying step")
                continue

        # --- QC output ---
        print("\n--- QC REPORT ---")
        print(audit["qc_report"])

        # --- Optional CTA interaction ---
        # clicked = click_by_text(page, ["shop now", "view collection"])
        # if clicked:
        #     print("[AGENT] CTA clicked")

        # --- Scroll ---
        if not scroll_page(page):
            print("[AGENT] Cannot scroll further, ending audit")
            break


if __name__ == "__main__":
    # CHANGE URL HERE
    run("https://bomcrewmall.com")
