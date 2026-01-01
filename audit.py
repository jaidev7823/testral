import base64
import ollama
import re


def run_audit(screenshot_path: str):
    """
    Pure perception module.

    Input:
        screenshot_path: str

    Output:
        {
            "qc_report": str,
            "blocker_hint": {
                "suspected": bool,
                "hint_text": str | None
            }
        }
    """

    # --- Load audit prompt ---
    with open("prompt/audit.txt", "r", encoding="utf-8") as f:
        audit_prompt = f.read()

    # --- Read image ---
    with open(screenshot_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    # --- Vision call ---
    response = ollama.chat(
        model="qwen3-vl",
        messages=[{
            "role": "user",
            "content": audit_prompt,
            "images": [image_b64]
        }]
    )

    qc_text = response["message"]["content"]

    # --- New blocker hint extraction ---
    blocker_hint = {
        "suspected": False,
        "close_button_text": None,
        "close_button_icon": None,
    }

    try:
        # Use regex to find the BLOCKER_HINT block
        hint_block_match = re.search(r"\[BLOCKER_HINT\](.*?)\[/BLOCKER_HINT\]", qc_text, re.DOTALL)
        if hint_block_match:
            hint_content = hint_block_match.group(1)

            # Extract values from the block
            suspected_match = re.search(r"SUSPECTED:\s*(YES|NO)", hint_content, re.IGNORECASE)
            if suspected_match and suspected_match.group(1).upper() == "YES":
                blocker_hint["suspected"] = True

            text_match = re.search(r"CLOSE_BUTTON_TEXT:\s*\"(.*?)\"", hint_content, re.IGNORECASE)
            if text_match and text_match.group(1):
                blocker_hint["close_button_text"] = text_match.group(1).strip().lower()

            icon_match = re.search(r"CLOSE_BUTTON_ICON:\s*\"(.*?)\"", hint_content, re.IGNORECASE)
            if icon_match and icon_match.group(1):
                blocker_hint["close_button_icon"] = icon_match.group(1).strip().lower()
            
            # Clean the main report text by removing the hint block
            qc_report = qc_text.replace(hint_block_match.group(0), "").strip()
        else:
            # If no block is found, the original text is the report
            qc_report = qc_text
    except Exception:
        # In case of any parsing error, just use the full text as the report
        qc_report = qc_text


    return {
        "qc_report": qc_report,
        "blocker_hint": blocker_hint
    }

