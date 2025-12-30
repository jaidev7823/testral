from tests import TESTS
from browser import get_page
from gemini import explain_failure
from pathlib import Path

Path("screenshots").mkdir(exist_ok=True)

results = []
passed = 0

for test in TESTS:
    mobile = test["id"] == "TC09"
    p, browser, page = get_page(TARGET_URL, mobile)

    fn = globals()[test["run"]]
    success = fn(page)

    entry = {
        "id": test["id"],
        "name": test["name"],
        "result": "Pass" if success else "Fail"
    }

    if not success:
        img = capture_failure(page, test["id"])
        entry["screenshot"] = img
        entry["explanation"] = explain_failure(img, test["name"])
    else:
        passed += 1

    results.append(entry)
    browser.close()
    p.stop()
