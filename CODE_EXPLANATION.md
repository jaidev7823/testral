# Code Explanation - What Each File Does

## 📁 agent.py
**Main orchestrator** - Controls the entire audit workflow

**What it does:**
1. Opens the browser and navigates to the URL
2. Loops through the page step-by-step:
   - Maps all clickable elements (gets element_map)
   - Takes a screenshot of current viewport
   - Runs AI audit on the screenshot
   - Saves audit results to `audit.md`
   - If blocker detected → tries to close it → re-audits
   - Scrolls down to next section
3. Continues until end of page
4. **Never aborts** - continues even if blocker can't be closed

**Key functions:**
- `run(url)` - Main entry point
- `_append_audit_to_file()` - Writes audit results to markdown file

---

## 📁 actions.py
**Element detection and blocker closing** - Finds clickable elements and closes blockers

**What it does:**
1. `get_clickable_map(page)` - Scans page for all clickable elements:
   - Finds buttons, links, inputs, etc.
   - Assigns each a unique `data-ai-idx` attribute
   - Returns list with: id, tag, text, aria-label, position
   - This map is sent to AI so it can reference elements by ID

2. `close_blocker(page, blocker_hint)` - Attempts to close blockers:
   - **Primary method**: Uses `close_button_idx` from AI to click element
   - **Fallback method**: Searches by text if ID method fails
   - Returns True if successful, False if failed

**Why it matters:**
- The AI needs the element map to provide the correct `close_button_idx`
- Without the ID, the system can't reliably click the close button

---

## 📁 audit.py
**AI vision analysis** - Sends screenshot to AI and extracts blocker info

**What it does:**
1. `run_audit(screenshot_path, element_map)`:
   - Reads the audit prompt from `prompt/audit.txt`
   - Sends screenshot + element_map to Ollama (qwen3-vl model)
   - AI analyzes screenshot and looks for blockers
   - Extracts `[BLOCKER_HINT]` section from AI response
   - Parses: `SUSPECTED`, `CLOSE_BUTTON_IDX`, `CLOSE_BUTTON_TEXT`
   - Returns: `{"qc_report": "...", "blocker_hint": {...}}`

**Critical parsing:**
- Looks for `CLOSE_BUTTON_IDX: <number>` in AI response
- This number must match an ID from the element_map
- If AI doesn't provide ID, blocker closing will fail

---

## 📁 browser.py
**Playwright browser control** - Handles browser operations

**What it does:**
1. `open_page(url)` - Launches browser, opens URL, waits for page load
2. `take_screenshot(page, name)` - Takes viewport screenshot, saves to `screenshots/`
3. `scroll_page(page)` - Scrolls down 600px, returns False if can't scroll more

---

## 🔧 The Bug That Was Fixed

### Problem:
- `prompt/audit.txt` didn't ask AI for `CLOSE_BUTTON_IDX`
- AI was only providing `CLOSE_BUTTON_TEXT` and `CLOSE_BUTTON_ICON`
- `audit.py` was looking for `CLOSE_BUTTON_IDX` but couldn't find it
- `close_blocker()` failed because `close_button_idx` was always `None`
- Agent continued but blocker never got closed

### Fix:
1. Updated `prompt/audit.txt` to **require** `CLOSE_BUTTON_IDX`
2. Prompt now tells AI to match close button to element_map IDs
3. Improved error handling in `close_blocker()` with better fallback
4. Added better debugging/logging throughout
5. Agent now continues even if blocker can't be closed (doesn't abort)

---

## 🔄 Workflow Flow

```
1. agent.py:run() starts
   ↓
2. browser.py:open_page() → opens website
   ↓
3. LOOP (for each section):
   ↓
4. actions.py:get_clickable_map() → finds all clickable elements
   ↓
5. browser.py:take_screenshot() → captures viewport
   ↓
6. audit.py:run_audit() → AI analyzes screenshot
   ↓
7. AI returns: blocker_hint with CLOSE_BUTTON_IDX
   ↓
8. If blocker detected:
   → actions.py:close_blocker() → clicks element by ID
   → Re-audit the cleared view
   ↓
9. agent.py:_append_audit_to_file() → saves results
   ↓
10. browser.py:scroll_page() → scrolls down
   ↓
11. Repeat until end of page
```

---

## ⚠️ Important Notes

- **Element Map is Critical**: AI must match close buttons to element_map IDs
- **Never Aborts**: Agent continues even if blocker can't be closed
- **Screenshots**: Only viewport screenshots (not full page)
- **Audit Log**: Appends to `audit.md` for each step

