import os
import json
import base64
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env
load_dotenv()

# 1. SETUP
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-computer-use-preview-10-2025"

def run_testral_audit(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        page.goto(url)
        
        report_file = open("audit_report.md", "w")
        report_file.write(f"# UX Audit Report for {url}\n\n")
        
        current_scroll = 0
        max_scroll = page.evaluate("document.body.scrollHeight")
        step = 1

        while current_scroll < max_scroll:
            print(f"Scanning Section {step}...")
            
            # 2. TAKE SCREENSHOT
            screenshot_path = f"reports/section_{step}.png"
            os.makedirs("reports", exist_ok=True)
            page.screenshot(path=screenshot_path)
            
            with open(screenshot_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")

            # 3. ASK GEMINI TO ANALYZE
            prompt = """
            Analyze this specific section of the webpage.
            Identify any 'Glitches' (UI overlaps, broken icons, grammar, trust gaps).
            Format the response as a list of findings.
            """
            
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    types.Part.from_bytes(data=base64.b64decode(img_data), mime_type="image/png"),
                    prompt
                ]
            )

            # 4. DOCUMENT FINDINGS
            report_file.write(f"## Section {step}\n")
            report_file.write(f"![Section {step}]({screenshot_path})\n\n")
            report_file.write(f"{response.text}\n\n---\n")

            # 5. SCROLL DOWN
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(1000) # Wait for animations
            current_scroll += 800
            step += 1
            
        browser.close()
        report_file.close()
        print("Audit Complete. See audit_report.md")

if __name__ == "__main__":
    run_testral_audit("https://bomcrewmall.com")