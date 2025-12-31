import sys
import base64
import os
from playwright.sync_api import sync_playwright
import ollama

def run_audit(url: str):
    # --- SETUP FOLDERS ---
    screenshot_dir = "screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    
    screenshot_path = os.path.join(screenshot_dir, "first_section.png")

    # --- LOAD PROMPT FROM FILE ---
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            prompt_content = f.read()
    except FileNotFoundError:
        print("Error: prompt.txt file not found. Please create it in the same directory.")
        return

    # --- PLAYWRIGHT SECTION ---
    with sync_playwright() as p:
        print(f"Opening browser for: {url}...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        # 1. Open site
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")

            # 2. Screenshot first visible section
            page.screenshot(path=screenshot_path, full_page=False)
            print(f"Screenshot saved to: {screenshot_path}")
        except Exception as e:
            print(f"Error during browser navigation: {e}")
            browser.close()
            return

        browser.close()

    # --- OLLAMA SECTION ---
    with open(screenshot_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    print("Sending image to Gemma-3 via Ollama...")
    response = ollama.chat(
        model="qwen3-vl",
        messages=[{
            "role": "user",
            "content": prompt_content,
            "images": [image_b64]
        }]
    )

    print("\n--- QC RESULT ---")
    print(response["message"]["content"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit.py <url>")
    else:
        run_audit(sys.argv[1])