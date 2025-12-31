from playwright.sync_api import sync_playwright
import os

class BrowserHelper:
    def __init__(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    def navigate_and_screenshot(self, url, name):
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        path = f"screenshots/{name}"
        self.page.screenshot(path=path, full_page=True)
        return path

    def take_screenshot(self, name):
        path = f"screenshots/{name}"
        self.page.screenshot(path=path, full_page=True)
        return path

    def close(self):
        self.browser.close()
        self.pw.stop()