from playwright.sync_api import TimeoutError, Error
import time


CLICKABLE_SELECTOR = "a, button, input[type=submit], [role=button]"


def _collect_clickables(page):
    elements = page.locator(CLICKABLE_SELECTOR)
    results = []

    for i in range(elements.count()):
        el = elements.nth(i)
        try:
            if not el.is_visible():
                continue

            box = el.bounding_box()
            if not box or box["width"] == 0 or box["height"] == 0:
                continue

            results.append({
                "element": el,
                "text": (el.inner_text() or "").strip().lower(),
                "aria": (el.get_attribute("aria-label") or "").strip().lower(),
                "y": box["y"]
            })
        except Exception:
            continue

    # Top-to-bottom priority
    results.sort(key=lambda x: x["y"])
    return results


def close_blocker(page, blocker_hint):
    """
    blocker_hint:
        {
            "suspected": bool,
            "close_button_text": str | None,
            "close_button_icon": str | None
        }
    """
    if not blocker_hint or not blocker_hint.get("suspected"):
        return False

    # Build a dynamic list of keywords from the audit hint
    keywords = []
    
    btn_text = blocker_hint.get("close_button_text")
    if btn_text:
        keywords.append(btn_text.lower())

    icon_desc = blocker_hint.get("close_button_icon")
    if icon_desc:
        # If the audit describes an 'x' or 'close' icon, search for
        # corresponding text in aria-labels for accessibility.
        if "x" in icon_desc.lower() or "close" in icon_desc.lower():
            keywords.append("close")
            keywords.append("x")

    # Add some very common, safe fallbacks in case the audit hint is weak
    keywords += ["accept", "agree", "got it", "continue", "ok", "no thanks", "close"]

    # Deduplicate while preserving order
    keywords = list(dict.fromkeys(keywords))
    
    # Filter out any empty keywords that might have slipped in
    keywords = [kw for kw in keywords if kw]

    for item in _collect_clickables(page):
        for kw in keywords:
            # Check against the element's visible text or its aria-label
            if kw in item["text"] or kw in item["aria"]:
                try:
                    item["element"].scroll_into_view_if_needed()
                    time.sleep(0.2)

                    try:
                        item["element"].click(timeout=3000)
                    except (TimeoutError, Error):
                        item["element"].click(force=True, timeout=3000)

                    page.wait_for_timeout(800)
                    return True
                except Exception:
                    continue
    
    return False


def click_by_text(page, target_texts):
    """
    target_texts: string or list of strings
    """

    if isinstance(target_texts, str):
        targets = [target_texts.lower()]
    else:
        targets = [t.lower() for t in target_texts]

    for item in _collect_clickables(page):
        for t in targets:
            if t in item["text"] or t in item["aria"]:
                try:
                    item["element"].scroll_into_view_if_needed()
                    time.sleep(0.2)

                    before_url = page.url
                    before_body = page.evaluate("() => document.body.innerText") or ""

                    # Perform the click. Use a short timeout for the click itself.
                    try:
                        item["element"].click(timeout=1000)
                    except (TimeoutError, Error):
                        # If regular click fails (e.g., element covered), try force click
                        item["element"].click(force=True, timeout=1000)
                    except Exception as e:
                        # Catch any other exception during click and continue to next item
                        print(f"Error during click: {e}")
                        continue

                    # Wait for potential changes to settle (navigation, DOM updates)
                    # Use a short timeout for load state, otherwise a fixed wait.
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=1500)
                    except TimeoutError:
                        # If domcontentloaded doesn't happen fast, just proceed
                        pass
                    page.wait_for_timeout(500) # Additional small wait

                    after_url = page.url
                    after_body = page.evaluate("() => document.body.innerText") or ""

                    # Determine if a meaningful change occurred
                    if before_url != after_url:
                        return True
                    if before_body != after_body:
                        return True

                    # Silent click — no meaningful change
                    return False
                except Exception:
                    continue

    return False
