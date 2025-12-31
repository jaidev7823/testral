class InteractionEngine:
    def __init__(self, browser):
        self.browser = browser

    def handle_blocker(self, btn_config):
        if not btn_config['exists']:
            return False
            
        # Critical DOM Interaction Rule
        hints = btn_config['likely_text']
        selectors = ["button", "div", "span", "svg", "img"]
        
        for selector in selectors:
            elements = self.browser.page.query_selector_all(selector)
            for el in elements:
                # Check text, aria-label, title
                text = (el.inner_text() or "").lower()
                aria = (el.get_attribute("aria-label") or "").lower()
                title = (el.get_attribute("title") or "").lower()
                
                if any(h in text or h in aria or h in title for h in hints):
                    print(f"✅ Found match: clicking {selector}")
                    el.click()
                    self.browser.page.wait_for_timeout(1000)
                    return True
        return False