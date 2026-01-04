# audit.py
import base64
import ollama
from pathlib import Path
from PIL import Image, ImageFilter
import re

BLOCKER_MODEL = "ministral-3"   # or gemma3:vision
AUDIT_MODEL = "devstral-small-2"
AUDIT_FILE = "audit.md"

AUDIT_PROMPT = Path("prompt/audit.txt").read_text(encoding="utf-8")
BLOCKER_DETECTION_PROMPT = Path("prompt/blocker-detection.txt").read_text(encoding="utf-8")
BLOCKER_PROMPT = Path("prompt/blocker.txt").read_text(encoding="utf-8")


def downscale_image(src_path: str, max_width: int = 960, sharpen: bool = True) -> str:
    src = Path(src_path)
    out = src.with_name(src.stem + ".png")

    img = Image.open(src).convert("RGB")
    w, h = img.size

    if w > max_width:
        scale = max_width / w
        img = img.resize((max_width, int(h * scale)), Image.LANCZOS)

    if sharpen:
        img = img.filter(
            ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=3)
        )

    img.save(out, optimize=True)
    return str(out)


def vision_call_audit(prompt: str, image_path: str) -> str:
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = ollama.chat(
        model=AUDIT_MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [img]
        }],
        options={"temperature": 0},
        stream=False
    )

    return response["message"]["content"] or ""


def vision_call_blocker(prompt: str, image_path: str) -> str:
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = ollama.chat(
        model=BLOCKER_MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [img]
        }],
        options={"temperature": 0},
        stream=False
    )
    print(response)
    return response["message"]["content"] or ""


def log(title, img, text):
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(f"## {title}\n")
        f.write(f"- Screenshot: {img}\n\n")
        f.write("```\n")
        f.write(text.strip() if text else "<EMPTY OUTPUT>")
        f.write("\n```\n\n---\n\n")


def parse_blocker_response(text: str):
    """
    Returns (blocked: bool, details: str | None)
    """
    if not text:
        return False, None

    blocked = "SUSPECTED: YES" in text

    details = None
    if blocked:
        m = re.search(r"DETAILS:\s*(.+)", text, re.I | re.S)
        if m:
            details = m.group(1).strip()

    return blocked, details



def run_audit(step, image, suffix="Initial"):
    print(f"[STEP {step}] Blocker check ({suffix})")

    ds_image = downscale_image(image)

    # ---- CALL 1: BLOCKER ONLY ----
    blocker_raw = vision_call_blocker(BLOCKER_DETECTION_PROMPT, ds_image)
    blocked, blocker_details = parse_blocker_response(blocker_raw)

    log(
        f"Step {step} — {suffix} Blocker Check",
        image,
        blocker_raw
    )

    if blocked:
        return blocker_details, True

    # ---- CALL 2: AUDIT ONLY ----
    print(f"[STEP {step}] Running audit ({suffix})")
    audit_raw = vision_call_audit(AUDIT_PROMPT, ds_image)

    log(
        f"Step {step} — {suffix} Audit",
        image,
        audit_raw
    )

    return audit_raw, False

def run_blocker_audit(step, image, details: str | None = None):
    print(f"[STEP {step}] Running blocker grounding")

    ds_image = downscale_image(image)
    prompt = BLOCKER_PROMPT

    if details:
        prompt = (
            prompt
            + "\n\n[BLOCKER_DESCRIPTION]\n"
            + details
            + "\n[/BLOCKER_DESCRIPTION]\n"
        )
    print(prompt)
    raw = vision_call_blocker(prompt, ds_image)

    print("[BLOCKER RAW]")
    print(raw)

    idx = parse_close_number(raw)

    log(
        f"Step {step} — Blocker Grounding",
        image,
        raw + f"\n\n[CLOSE_NUMBER]: {idx}"
    )

    return idx


def parse_close_number(text: str):
    match = re.search(r"CLOSE_NUMBER:\s*(\d+)", text)
    return int(match.group(1)) if match else None
